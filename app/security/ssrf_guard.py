import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional

# Reserved and private network blocks (IPv4 + IPv6)
BLOCKED_NETWORKS = [
    # IPv4 loopback & private
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    # Cloud Instance Metadata Service (AWS, GCP, Azure, DigitalOcean, Alibaba)
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),   # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"), # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),     # Multicast
    ipaddress.ip_network("240.0.0.0/4"),     # Reserved/broadcast
    # IPv6 loopback, link-local, unique local
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),        # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),       # Link-local
    ipaddress.ip_network("::ffff:0:0/96"),   # IPv4-mapped IPv6
]

ALLOWED_SCHEMES = {"http", "https"}


class SSRFValidationError(ValueError):
    """Raised when an outgoing URL target violates Anti-SSRF policy."""
    pass


def validate_target_url(raw_url: str) -> Tuple[str, str]:
    """
    Validates a target URL against SSRF vulnerabilities:
    1. Validates scheme (strictly http/https).
    2. Resolves DNS hostname to physical IP addresses.
    3. Blocks localhost, internal RFC1918, link-local, and cloud IMDS (169.254.169.254).
    4. Returns tuple (clean_url, resolved_ip).
    """
    if not raw_url or not isinstance(raw_url, str):
        raise SSRFValidationError("URL cannot be empty.")

    raw_url = raw_url.strip()
    parsed = urlparse(raw_url)
    scheme = parsed.scheme.lower() if parsed.scheme else ""

    if scheme and scheme not in ALLOWED_SCHEMES:
        raise SSRFValidationError(f"Protocol '{scheme}' is prohibited. Only HTTP and HTTPS are permitted.")

    if not scheme:
        raw_url = "https://" + raw_url
        parsed = urlparse(raw_url)
        scheme = parsed.scheme.lower()

    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("Invalid target URL: missing hostname.")

    # Lowercase hostname check for known metadata names
    lower_host = hostname.lower().strip("[]")
    if lower_host in ("localhost", "metadata.google.internal", "instance-data"):
        raise SSRFValidationError(f"Access to '{hostname}' is blocked by Anti-SSRF security policies.")

    # Resolve all IPs for hostname
    try:
        addr_infos = socket.getaddrinfo(lower_host, parsed.port or (443 if scheme == "https" else 80))
    except socket.gaierror as e:
        raise SSRFValidationError(f"Could not resolve host '{hostname}': {e}")

    resolved_ips = {item[4][0] for item in addr_infos}
    if not resolved_ips:
        raise SSRFValidationError(f"No IP addresses resolved for '{hostname}'.")

    # Inspect each resolved IP against blocked networks
    for ip_str in resolved_ips:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFValidationError(f"Invalid IP address resolved: {ip_str}")

        # Check against private / loopback / link-local / cloud metadata
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
            raise SSRFValidationError(
                f"Access to private/internal IP address '{ip_str}' is blocked by Anti-SSRF security policies."
            )

        for blocked_net in BLOCKED_NETWORKS:
            if ip_obj in blocked_net:
                raise SSRFValidationError(
                    f"Access to IP address '{ip_str}' in restricted network {blocked_net} is blocked."
                )

    # Return validated URL and primary resolved IP
    return raw_url, sorted(list(resolved_ips))[0]
