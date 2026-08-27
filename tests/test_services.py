import io
import pytest
from app.services.math_service import safe_calculate, MathEvaluationError
from app.services.password_service import (
    analyze_password,
    generate_passphrase,
    generate_secure_password,
    mask_password,
    calculate_entropy,
)
from app.services.note_service import compute_reading_stats, render_markdown_to_html
from app.services.analytics_service import parse_csv_bytes
from app.services.color_service import (
    calculate_contrast_ratio,
    export_tailwind_palette,
    generate_color_palette,
    hex_to_rgb,
    rgb_to_hex,
)
from app.services.url_service import (
    generate_qr_code_bytes,
    generate_short_code,
    is_valid_url,
    normalize_url,
)
from app.services.file_service import process_image, merge_pdfs, split_or_extract_pdf_pages
from PIL import Image
import pypdf


class TestMathService:
    def test_basic_and_scientific_math(self):
        assert safe_calculate("2 + 2") == "4"
        assert safe_calculate("sqrt(64)") == "8"
        assert safe_calculate("factorial(5)") == "120"
        assert safe_calculate("log(100)") == "2"
        assert float(safe_calculate("ln(e)")) == pytest.approx(1.0, 0.01)

    def test_trigonometry_modes(self):
        # sin(pi/2) in rad == 1
        assert float(safe_calculate("sin(pi / 2)", angle_mode="rad")) == pytest.approx(1.0, 0.01)
        # sin(90) in deg == 1
        assert float(safe_calculate("sin(90)", angle_mode="deg")) == pytest.approx(1.0, 0.01)

    def test_division_by_zero_and_security(self):
        with pytest.raises(MathEvaluationError, match="Division by zero"):
            safe_calculate("10 / 0")

        with pytest.raises(MathEvaluationError):
            safe_calculate("__import__('os').system('ls')")


class TestPasswordService:
    def test_entropy_and_strength(self):
        assert calculate_entropy("") == 0.0
        entropy = calculate_entropy("StrongPassword123!#")
        assert entropy >= 70.0

        res_weak = analyze_password("123456")
        assert res_weak["is_breached"] is True
        assert res_weak["strength"] == "Very Weak"

        res_strong = analyze_password("Correct-Horse-Battery-Staple-2026!")
        assert res_strong["score"] >= 80

    def test_generators(self):
        pwd = generate_secure_password(length=20)
        assert len(pwd) == 20

        passphrase = generate_passphrase(word_count=4)
        assert len(passphrase.split("-")) >= 4


class TestNoteService:
    def test_markdown_rendering(self):
        html = render_markdown_to_html("# Heading\n\n**Bold Text**")
        assert "Heading</h1>" in html
        assert "<strong>Bold Text</strong>" in html

    def test_reading_stats(self):
        stats = compute_reading_stats("The quick brown fox jumps over the lazy dog.")
        assert stats["words"] == 9
        assert stats["reading_time_min"] == 1


class TestAnalyticsService:
    def test_pandas_csv_profiling(self):
        csv_data = b"name,age,salary,department\nAlice,30,75000,Engineering\nBob,40,95000,Sales\nCharlie,35,82000,Engineering\nDavid,28,60000,Sales\n"
        profile = parse_csv_bytes(csv_data)
        assert profile["overview"]["row_count"] == 4
        assert profile["overview"]["col_count"] == 4
        assert "salary" in profile["numeric_stats"]
        assert profile["numeric_stats"]["salary"]["mean"] == 78000.0


class TestColorService:
    def test_palette_and_contrast(self):
        palette = generate_color_palette("#4f46e5", "Complementary")
        assert len(palette) == 5

        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio == 21.0

        tailwind = export_tailwind_palette(["#4f46e5", "#10b981"])
        assert "module.exports" in tailwind


class TestUrlService:
    def test_url_and_qr(self):
        assert is_valid_url("https://github.com") is True
        assert normalize_url("google.com") == "https://google.com"

        code = generate_short_code(6)
        assert len(code) == 6

        qr_png, mime_png = generate_qr_code_bytes("https://github.com", format_type="png")
        assert mime_png == "image/png"
        assert len(qr_png) > 100


class TestFileService:
    def test_image_processing(self):
        # Create a test image
        img = Image.new("RGB", (100, 100), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_img = buf.getvalue()

        out_bytes, ext, mime = process_image(raw_img, action="resize", width=50, height=50, target_format="jpg")
        assert ext == "jpg"
        assert mime == "image/jpeg"
        assert len(out_bytes) > 0

    def test_pdf_operations(self):
        # Create minimal PDF
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        buf1 = io.BytesIO()
        writer.write(buf1)
        pdf1 = buf1.getvalue()

        # Merge 2 PDFs
        merged = merge_pdfs([pdf1, pdf1])
        reader = pypdf.PdfReader(io.BytesIO(merged))
        assert len(reader.pages) == 2

        # Extract page 1
        extracted = split_or_extract_pdf_pages(merged, [1])
        reader_ext = pypdf.PdfReader(io.BytesIO(extracted))
        assert len(reader_ext.pages) == 1
