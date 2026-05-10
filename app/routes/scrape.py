from flask import Blueprint, request, jsonify
from app.collectors.channel_scraper import ChannelScraper

bp = Blueprint("scrape", __name__)

@bp.route("/scrape-channel", methods=["POST"])
def scrape_channel():
    data = request.json
    channel_url = data.get("url")
    
    scraper = ChannelScraper()
    videos = scraper.scrape_channel(channel_url, max_videos=500)
    
    return jsonify({
        "success": True,
        "channel": channel_url,
        "total_videos": len(videos),
        "videos": videos
    })