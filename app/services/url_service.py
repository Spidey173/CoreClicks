import io
import re
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, Tuple
import qrcode
from qrcode.image.svg import SvgPathImage

URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def is_valid_url(url: str) -> bool:
    """Validates URL format."""
    if not url or len(url) > 2048:
        return False
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return bool(URL_REGEX.match(url))


def normalize_url(url: str) -> str:
    """Ensures URL starts with https:// if protocol is missing."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def generate_short_code(length: int = 6) -> str:
    """Generates a random URL-safe alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_qr_code_bytes(url: str, format_type: str = "png") -> Tuple[bytes, str]:
    """
    Generates QR code bytes for a short URL in PNG or SVG format.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    if format_type.lower() == "svg":
        img = qr.make_image(image_factory=SvgPathImage)
        out = io.BytesIO()
        img.save(out)
        return out.getvalue(), "image/svg+xml"
    else:
        img = qr.make_image(fill_color="black", back_color="white")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue(), "image/png"
