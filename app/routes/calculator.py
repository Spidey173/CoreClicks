from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.calculation import Calculation
from app.services.math_service import MathEvaluationError, safe_calculate
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

calculator_bp = Blueprint("calculator", __name__)


@calculator_bp.route("/calculator")
@login_required
def view():
    return render_template("tools/calculator.html")


@calculator_bp.route("/api/v1/calculator/calculate", methods=["POST"])
@api_or_login_required
def calculate():
    user_id = current_user.id if current_user.is_authenticated else request.user_id
    data = request.get_json(silent=True) or {}
    expression = data.get("expression", "").strip()
    angle_mode = data.get("angle_mode", "rad")

    if not expression:
        return jsonify({"status": "error", "message": "Expression cannot be empty."}), 400

    try:
        result_str = safe_calculate(expression, angle_mode=angle_mode)

        # Log calculation
        calc = Calculation(
            user_id=user_id,
            expression=expression,
            result=result_str,
            mode=angle_mode,
        )
        db.session.add(calc)
        db.session.commit()

        log_activity(user_id, "calculation", "calculator", f"{expression} = {result_str}")

        return jsonify({
            "status": "success",
            "expression": expression,
            "result": result_str,
            "angle_mode": angle_mode,
            "id": calc.id,
        }), 201

    except MathEvaluationError as me:
        return jsonify({"status": "error", "message": str(me)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Calculation error: {str(e)}"}), 500


@calculator_bp.route("/api/v1/calculator/history", methods=["GET"])
@api_or_login_required
def get_history():
    user_id = current_user.id
    calcs = Calculation.query.filter_by(user_id=user_id).order_by(Calculation.created_at.desc()).limit(25).all()
    return jsonify([c.to_dict() for c in calcs])


@calculator_bp.route("/api/v1/calculator/history", methods=["DELETE"])
@api_or_login_required
def clear_history():
    user_id = current_user.id
    Calculation.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"status": "success", "message": "Calculation history cleared."})
