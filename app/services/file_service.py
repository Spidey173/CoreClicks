import io
import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import pypdf


def process_image(
    image_bytes: bytes,
    action: str = "convert",
    target_format: str = "png",
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 85,
    rotation_angle: int = 0,
    crop_box: Optional[Tuple[int, int, int, int]] = None,
    watermark_text: Optional[str] = None,
) -> Tuple[bytes, str, str]:
    """
    Applies transformations on image bytes and returns (result_bytes, extension, mime_type).
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convert mode for PNG/WebP with alpha vs JPG
    target_fmt = target_format.lower().strip()
    if target_fmt in ("jpg", "jpeg"):
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        ext = "jpg"
        mime = "image/jpeg"
        save_fmt = "JPEG"
    elif target_fmt == "webp":
        ext = "webp"
        mime = "image/webp"
        save_fmt = "WEBP"
    else:
        ext = "png"
        mime = "image/png"
        save_fmt = "PNG"

    # Crop
    if crop_box and len(crop_box) == 4:
        img = img.crop(crop_box)

    # Resize
    if width and height and width > 0 and height > 0:
        img = img.resize((min(4000, width), min(4000, height)), Image.Resampling.LANCZOS)
    elif width and width > 0:
        ratio = width / img.width
        img = img.resize((min(4000, width), int(img.height * ratio)), Image.Resampling.LANCZOS)
    elif height and height > 0:
        ratio = height / img.height
        img = img.resize((int(img.width * ratio), min(4000, height)), Image.Resampling.LANCZOS)

    # Rotate
    if rotation_angle in (90, 180, 270):
        img = img.rotate(-rotation_angle, expand=True)

    # Watermark
    if watermark_text and watermark_text.strip():
        draw = ImageDraw.Draw(img)
        text = watermark_text.strip()
        # Draw semi-transparent watermark in bottom-right corner
        draw.text((max(10, img.width - 200), max(10, img.height - 40)), text, fill=(200, 200, 200))

    out_io = io.BytesIO()
    if save_fmt == "JPEG":
        img.save(out_io, format=save_fmt, quality=max(10, min(100, quality)), optimize=True)
    elif save_fmt == "WEBP":
        img.save(out_io, format=save_fmt, quality=max(10, min(100, quality)), method=6)
    else:
        img.save(out_io, format=save_fmt, optimize=True)

    return out_io.getvalue(), ext, mime


def merge_pdfs(pdf_bytes_list: List[bytes]) -> bytes:
    """Merges a list of PDF byte streams into a single PDF."""
    writer = pypdf.PdfWriter()
    for b in pdf_bytes_list:
        reader = pypdf.PdfReader(io.BytesIO(b))
        writer.append(reader)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def split_or_extract_pdf_pages(pdf_bytes: bytes, pages: List[int]) -> bytes:
    """Extracts specific page numbers (1-indexed) into a new PDF."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    total = len(reader.pages)
    for p in pages:
        idx = p - 1
        if 0 <= idx < total:
            writer.add_page(reader.pages[idx])

    out_io = io.BytesIO()
    writer.write(out_io)
    return out_io.getvalue()


def protect_pdf_with_password(pdf_bytes: bytes, password: str) -> bytes:
    """Encrypts a PDF with user password."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)
    out_io = io.BytesIO()
    writer.write(out_io)
    return out_io.getvalue()


def inspect_pdf_metadata(pdf_bytes: bytes) -> Dict[str, Any]:
    """Extracts page count, author, title, and encryption status of a PDF."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    meta = reader.metadata or {}

    return {
        "page_count": len(reader.pages),
        "is_encrypted": reader.is_encrypted,
        "title": meta.title if meta.title else "Untitled Document",
        "author": meta.author if meta.author else "Unknown",
        "producer": meta.producer if meta.producer else "PDF Producer",
    }
