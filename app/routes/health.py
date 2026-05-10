from flask import Blueprint
import os

bp = Blueprint("health", __name__)

@bp.route("/health", methods=["GET"])
def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "collector": "yt-dlp" if os.getenv("USE_YTDLP") == "true" else "youtube-api"
    }
