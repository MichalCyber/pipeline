import yt_dlp
import logging
import os
from datetime import datetime
import re
import random
import time
from yt_dlp import YoutubeDL

def _human_delay():
    time.sleep(random.uniform(1.5, 7.0))

logger = logging.getLogger(__name__)

class YtDlpCollector:
    """YouTube Shorts collector using yt-dlp with fallback"""
    
    def __init__(self, cookies_file=None):
        if cookies_file is None:
            cookies_file = os.getenv('YTDLP_COOKIES_FILE', 'cookies.txt')
        
        self.cookies_file = cookies_file if os.path.exists(cookies_file) else None
        
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'socket_timeout': 30,
            'retries': 3,
        }
        
        if self.cookies_file:
            self.ydl_opts['cookiefile'] = self.cookies_file
            logger.info(f" Using cookies: {self.cookies_file}")
        else:
            logger.warning("  No cookies - engagement data may be limited")
            logger.info(" Tip: Export cookies.txt from browser")
    
    def search_shorts(self, query, max_results=50):
        try:
            # lepšie search varianty pre chinese drama
            search_query = f"{query} drama scene OR clip OR edit"
            search_url = f"ytsearch{max_results}:{search_query}"

            logger.info(f"yt-dlp search: '{search_query}' (max: {max_results})")

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)

            if not search_results or 'entries' not in search_results:
                logger.warning("No results from yt-dlp")
                return []

            posts = []
            for entry in search_results['entries']:
                if not entry:
                    continue

                video_info = self._extract_post_data(entry)
                if video_info:
                    posts.append(video_info)

            logger.info(f"Collected {len(posts)} videos via yt-dlp")
            return posts

        except Exception as e:
            logger.error(f"yt-dlp search failed: {e}")
            return []

            
        except Exception as e:
            logger.error(f" yt-dlp failed: {e}")
            return self._try_fallback(query, max_results)
    
    def _try_fallback(self, query, max_results):
        """Fallback to YouTube API if available"""
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not youtube_api_key:
            logger.warning("  No fallback available (YOUTUBE_API_KEY not set)")
            return []
        
        logger.info(" Falling back to YouTube API collector")
        
        try:
            from ..pipeline.collector import YouTubeShortsCollector
            fallback = YouTubeShortsCollector(youtube_api_key)
            return fallback.search_shorts(query, max_results)
        except Exception as e:
            logger.error(f" Fallback also failed: {e}")
            return []
    
    def _extract_post_data(self, entry):
        """Extract video metadata"""
        try:
            views = entry.get('view_count', 0) or 0
            likes = entry.get('like_count', 0) or 0
  
            if views == 0:
                logger.debug(f"Video {entry.get('id')} has no view count")
            
            title = entry.get('title', '').strip()
            description = entry.get('description', '')[:200].strip()
            caption = f"{title}. {description}"
            caption = re.sub(r'\s+', ' ', caption)
            
            return {
                'caption': caption,
                'title': title,
                'views': views,
                'likes': likes,
                'duration': entry.get('duration', 0),
                'timestamp': datetime.now().timestamp(),
                'video_id': entry.get('id', '')
            }
        except Exception as e:
            logger.error(f"Failed to extract data: {e}")
            return None
        
    def collect_videos(url, max_videos=500):
            ydl_opts = {
                "extract_flat": True,
                "skip_download": True,
                "quiet": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            videos = []
            for e in info.get("entries", []):
                if not e:
                    continue

                videos.append({
                    "video_id": e.get("id"),
                    "title": e.get("title"),
                    "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                    "duration": e.get("duration"),
                    "view_count": e.get("view_count"),
                    "upload_date": e.get("upload_date"),
                    "downloaded": False,
                    "downloaded_video": None
                })

            return videos
