from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.color_palette import ColorPalette
from app.services.color_service import (
    calculate_contrast_ratio,
    export_tailwind_palette,
    generate_color_palette,
)
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

color_tools_bp = Blueprint("color_tools", __name__)


@color_tools_bp.route("/color-tools")
@login_required
def view():
    return render_template("tools/color_tools.html")


@color_tools_bp.route("/api/v1/color-tools/generate", methods=["POST"])
@api_or_login_required
def generate():
    data = request.get_json(silent=True) or {}
    base_color = data.get("base_color", "#4f46e5").strip()
    harmony = data.get("harmony", "Complementary")

    palette = generate_color_palette(base_color, harmony)
    hex_list = [c["hex"] for c in palette]
    tailwind_config = export_tailwind_palette(hex_list)

    return jsonify({
        "status": "success",
        "base_color": base_color,
        "harmony": harmony,
        "palette": palette,
        "tailwind_config": tailwind_config,
    })


@color_tools_bp.route("/api/v1/color-tools/contrast", methods=["POST"])
@api_or_login_required
def contrast():
    data = request.get_json(silent=True) or {}
    fg = data.get("foreground", "#000000").strip()
    bg = data.get("background", "#ffffff").strip()

    ratio = calculate_contrast_ratio(fg, bg)
    return jsonify({
        "status": "success",
        "ratio": ratio,
        "wcag_aa_normal": ratio >= 4.5,
        "wcag_aa_large": ratio >= 3.0,
        "wcag_aaa_normal": ratio >= 7.0,
        "wcag_aaa_large": ratio >= 4.5,
    })


@color_tools_bp.route("/api/v1/color-tools/palettes", methods=["GET", "POST"])
@api_or_login_required
def palettes():
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Custom Palette").strip() or "Custom Palette"
        harmony = data.get("harmony_type", "Complementary")
        colors = data.get("colors", [])

        if not colors:
            return jsonify({"status": "error", "message": "Colors list is required."}), 400

        cp = ColorPalette(user_id=user_id, name=name, harmony_type=harmony)
        cp.colors = colors

        try:
            db.session.add(cp)
            db.session.commit()
            log_activity(user_id, "saved_palette", "color_tools", f"Saved palette: {name}")
            return jsonify({"status": "success", "palette": cp.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    saved = ColorPalette.query.filter_by(user_id=user_id).order_by(ColorPalette.created_at.desc()).all()
    return jsonify([p.to_dict() for p in saved])


@color_tools_bp.route("/api/v1/color-tools/palettes/<int:p_id>", methods=["DELETE"])
@api_or_login_required
def delete_palette(p_id):
    user_id = current_user.id
    cp = ColorPalette.query.filter_by(id=p_id, user_id=user_id).first_or_404()
    db.session.delete(cp)
    db.session.commit()
    return jsonify({"status": "success", "message": "Palette removed."})
