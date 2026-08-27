from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.services.search_service import global_omni_search
from app.utils.decorators import api_or_login_required

search_api_bp = Blueprint("api_search", __name__)


@search_api_bp.route("/api/v1/search", methods=["GET"])
@api_or_login_required
def search():
    query = request.args.get("q", "")
    results = global_omni_search(current_user.id, query)
    return jsonify({"status": "success", "query": query, "results": results})
