from flask import Blueprint

bp = Blueprint("stats", __name__)

@bp.route("/stats", methods=["GET"])
def stats():
    return {
        "status": "ok",
        "message": "Stats endpoint placeholder"
    }
