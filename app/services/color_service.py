import colorsys
from typing import Any, Dict, List, Tuple


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts HEX string to (R, G, B) tuple."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        return (0, 0, 0)
    try:
        return tuple(int(hex_clean[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts (R, G, B) to #RRGGBB hex string."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Converts (R, G, B) to (H, S, L)."""
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    return int(round(h * 360)), int(round(s * 100)), int(round(l * 100))


def hsl_to_rgb(h: int, s: int, l: int) -> Tuple[int, int, int]:
    """Converts (H, S, L) to (R, G, B)."""
    h_norm = (h % 360) / 360.0
    s_norm = max(0, min(100, s)) / 100.0
    l_norm = max(0, min(100, l)) / 100.0
    r_norm, g_norm, b_norm = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
    return int(round(r_norm * 255)), int(round(g_norm * 255)), int(round(b_norm * 255))


def get_relative_luminance(r: int, g: int, b: int) -> float:
    """Calculates WCAG 2.1 relative luminance for an sRGB color."""
    def adjust(c):
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4

    r_adj, g_adj, b_adj = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r_adj + 0.7152 * g_adj + 0.0722 * b_adj


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculates WCAG 2.1 contrast ratio between two colors (1.0 to 21.0)."""
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    l1 = get_relative_luminance(*rgb1)
    l2 = get_relative_luminance(*rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = (lighter + 0.05) / (darker + 0.05)
    return round(ratio, 2)


def generate_color_palette(base_hex: str, harmony_type: str = "Complementary") -> List[Dict[str, Any]]:
    """Generates a 5-color harmonious palette based on harmony rule."""
    rgb = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(*rgb)

    if harmony_type == "Complementary":
        hues = [h, (h + 30) % 360, (h + 180) % 360, (h + 210) % 360, (h + 330) % 360]
    elif harmony_type == "Analogous":
        hues = [(h - 40) % 360, (h - 20) % 360, h, (h + 20) % 360, (h + 40) % 360]
    elif harmony_type == "Triadic":
        hues = [h, (h + 60) % 360, (h + 120) % 360, (h + 240) % 360, (h + 300) % 360]
    elif harmony_type == "Tetradic":
        hues = [h, (h + 90) % 360, (h + 180) % 360, (h + 270) % 360, (h + 45) % 360]
    elif harmony_type == "Split-Complementary":
        hues = [h, (h + 150) % 360, (h + 210) % 360, (h + 30) % 360, (h + 180) % 360]
    elif harmony_type == "Monochromatic":
        hues = [h, h, h, h, h]
    else:  # Default / Balanced
        hues = [h, (h + 45) % 360, (h + 90) % 360, (h + 180) % 360, (h + 270) % 360]

    palette = []
    lightness_steps = [max(15, l - 25), max(25, l - 10), l, min(85, l + 15), min(95, l + 30)]

    for i in range(5):
        current_h = hues[i]
        current_l = lightness_steps[i] if harmony_type == "Monochromatic" else l
        current_s = s
        col_rgb = hsl_to_rgb(current_h, current_s, current_l)
        col_hex = rgb_to_hex(*col_rgb)
        col_hsl = (current_h, current_s, current_l)

        contrast_white = calculate_contrast_ratio(col_hex, "#ffffff")
        contrast_black = calculate_contrast_ratio(col_hex, "#000000")
        best_text = "#ffffff" if contrast_white >= contrast_black else "#000000"

        palette.append({
            "hex": col_hex,
            "rgb": f"rgb({col_rgb[0]}, {col_rgb[1]}, {col_rgb[2]})",
            "hsl": f"hsl({col_hsl[0]}, {col_hsl[1]}%, {col_hsl[2]}%)",
            "contrast_white": contrast_white,
            "contrast_black": contrast_black,
            "best_text": best_text,
            "wcag_aa": max(contrast_white, contrast_black) >= 4.5,
            "wcag_aaa": max(contrast_white, contrast_black) >= 7.0,
        })

    return palette


def export_tailwind_palette(colors: List[str]) -> str:
    """Formats list of HEX colors into a Tailwind CSS colors config object."""
    output = "module.exports = {\n  theme: {\n    extend: {\n      colors: {\n        brand: {\n"
    shades = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
    for i, c in enumerate(colors):
        shade = shades[i] if i < len(shades) else f"{i + 1}00"
        output += f"          '{shade}': '{c}',\n"
    output += "        }\n      }\n    }\n  }\n}"
    return output
