import time
import random
import logging
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# Collector facade
# ============================================================================

class Collector:
    def __init__(self):
        self.use_ytdlp = settings.USE_YTDLP
        self.youtube_api_key = settings.YOUTUBE_API_KEY

        if self.use_ytdlp:
            from yt_dlp import YoutubeDL
            self.ytdlp = YoutubeDL(self._ytdlp_opts())
            logger.info("Collector using yt-dlp")
        else:
            from googleapiclient.discovery import build
            self.youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
            logger.info("Collector using YouTube Data API")

    # ------------------------------------------------------------------------

    def collect(self, query: str, max_results: int = 50):
        if self.use_ytdlp:
            return self._collect_with_ytdlp(query, max_results)
        return self._collect_with_api(query, max_results)

    # ------------------------------------------------------------------------
    # YouTube API
    # ------------------------------------------------------------------------

    def _collect_with_api(self, query, max_results):
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            videoDuration="short",
            order="viewCount",
            maxResults=min(max_results, 50),
            publishedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        )
        response = request.execute()

        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        stats = self._fetch_video_stats(video_ids)

        results = []
        for item in response.get("items", []):
            vid = item["id"]["videoId"]
            s = stats.get(vid, {})

            results.append({
                "video_id": vid,
                "caption": item["snippet"]["title"],
                "views": s.get("views", 0),
                "likes": s.get("likes", 0),
                "comments": s.get("comments", 0),
                "timestamp": datetime.fromisoformat(
                    item["snippet"]["publishedAt"].replace("Z", "+00:00")
                ).timestamp()
            })
        return results

    # ------------------------------------------------------------------------
    # yt-dlp (anti-ban friendly)
    # ------------------------------------------------------------------------

    def _collect_with_ytdlp(self, query, max_results):
        search_url = f"ytsearch{max_results}:{query}"
        results = []

        for entry in self.ytdlp.extract_info(search_url, download=False)["entries"]:
            results.append({
                "video_id": entry["id"],
                "caption": entry.get("title", ""),
                "views": entry.get("view_count", 0),
                "likes": entry.get("like_count", 0),
                "duration": entry.get("duration", 0),
                "timestamp": entry.get("timestamp", time.time())
            })

            # anti-ban delay
            time.sleep(random.uniform(3, 7))

        return results
    def _fetch_video_stats(self, video_ids):
        response = self.youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(video_ids)
        ).execute()

        stats = {}
        for item in response.get("items", []):
            stats[item["id"]] = {
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "duration": item["contentDetails"]["duration"]
            }
        return stats

    # ------------------------------------------------------------------------

    def _ytdlp_opts(self):
        return {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "sleep_interval": 3,
            "max_sleep_interval": 7,
            "user_agent": random.choice(settings.USER_AGENTS),
        }
    
class YouTubeShortsCollector(Collector):
    """
    Alias for Collector.
    Exists only to keep imports stable:
         from app.pipeline.collector import YouTubeShortsCollector
    """
pass
