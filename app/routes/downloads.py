from flask import Blueprint, request, jsonify, g
from pathlib import Path
from app.collectors.profile_downloader import ProfileDownloader
from app.security import require_api_key
import logging

bp = Blueprint("download", __name__)
logger = logging.getLogger(__name__)


@bp.route("/download-profile", methods=["POST"])
@require_api_key
def download_profile():
    """
    Download videos from social media profile
    
    POST /download-profile
    {
        "profile_url": "https://www.tiktok.com/@username",
        "max_videos": 20,
        "download_videos": true,
        "cookies_platform": "tiktok"  // optional: tiktok, instagram, facebook
    }
    
    Returns:
    {
        "success": true,
        "request_id": "abc123",
        "profile_url": "...",
        "platform": "tiktok",
        "videos_count": 20,
        "videos": [...]
    }
    """
    
    data = request.json
    profile_url = data.get("profile_url")
    max_videos = data.get("max_videos", 50)
    download_videos = data.get("download_videos", True)
    cookies_platform = data.get("cookies_platform")
    
    if not profile_url:
        return jsonify({
            "success": False,
            "error": "profile_url is required"
        }), 400
    
    logger.info(f"[{g.request_id}] Download request: {profile_url}")
    
    # Setup cookies if specified
    cookies_file = None
    if cookies_platform:
        cookies_file = Path(f"cookies/{cookies_platform}_cookies.txt")
        if not cookies_file.exists():
            return jsonify({
                "success": False,
                "error": f"Cookies file not found: {cookies_file}"
            }), 400
    
    # Create output directory
    output_dir = Path(f"downloads/{g.request_id}")
    
    # Download
    try:
        downloader = ProfileDownloader(
            output_dir=output_dir,
            cookies_file=cookies_file
        )
        
        videos = downloader.download_profile(
            profile_url=profile_url,
            max_videos=max_videos,
            download_videos=download_videos
        )
        
        return jsonify({
            "success": True,
            "request_id": g.request_id,
            "profile_url": profile_url,
            "platform": downloader._detect_platform(profile_url),
            "videos_count": len(videos),
            "videos": videos,
            "output_dir": str(output_dir)
        })
    
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500