import base64
import json
import time
import requests
from typing import Any, Dict, Optional

TIMEOUT_SECONDS = 15
MAX_RESPONSE_SIZE = 4 * 1024 * 1024  # 4MB limit


def execute_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    auth_type: str = "none",
    auth_data: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Executes outgoing HTTP request with latency timing and response inspection.
    """
    method = method.upper().strip()
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
        method = "GET"

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    req_headers = {"User-Agent": "CoreClicks-ApiTester/2.0"}
    if headers and isinstance(headers, dict):
        req_headers.update(headers)

    # Auth configuration
    if auth_type == "bearer" and auth_data and "token" in auth_data:
        req_headers["Authorization"] = f"Bearer {auth_data['token'].strip()}"
    elif auth_type == "basic" and auth_data:
        user = auth_data.get("username", "")
        pwd = auth_data.get("password", "")
        encoded = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("utf-8")
        req_headers["Authorization"] = f"Basic {encoded}"
    elif auth_type == "apikey" and auth_data:
        key_name = auth_data.get("key", "X-API-Key")
        key_val = auth_data.get("value", "")
        req_headers[key_name] = key_val

    data_payload = None
    if body and method in ("POST", "PUT", "PATCH", "DELETE"):
        data_payload = body.encode("utf-8")
        if "Content-Type" not in req_headers:
            req_headers["Content-Type"] = "application/json"

    start_time = time.perf_counter()

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=req_headers,
            data=data_payload,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=True,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        content_bytes = resp.content[:MAX_RESPONSE_SIZE]
        try:
            resp_text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            resp_text = content_bytes.decode("latin-1", errors="replace")

        formatted_json = None
        if "json" in resp.headers.get("Content-Type", "").lower():
            try:
                formatted_json = json.loads(resp_text)
            except Exception:
                pass

        return {
            "success": 200 <= resp.status_code < 400,
            "status_code": resp.status_code,
            "status_text": resp.reason,
            "latency_ms": round(elapsed_ms, 1),
            "size_bytes": len(content_bytes),
            "content_type": resp.headers.get("Content-Type", ""),
            "headers": dict(resp.headers),
            "body": resp_text,
            "json_data": formatted_json,
        }

    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "status_code": 408,
            "status_text": "Request Timeout",
            "latency_ms": round(elapsed_ms, 1),
            "size_bytes": 0,
            "content_type": "text/plain",
            "headers": {},
            "body": f"Request timed out after {TIMEOUT_SECONDS} seconds.",
            "json_data": None,
        }
    except requests.exceptions.RequestException as re:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "status_code": 0,
            "status_text": "Connection Error",
            "latency_ms": round(elapsed_ms, 1),
            "size_bytes": 0,
            "content_type": "text/plain",
            "headers": {},
            "body": f"Connection Error: {str(re)}",
            "json_data": None,
        }
