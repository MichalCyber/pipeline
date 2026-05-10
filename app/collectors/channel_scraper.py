import yt_dlp
import logging

logger = logging.getLogger(__name__)

class ChannelScraper:
    """Scrape all videos from a YouTube channel"""
    
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # metadata only
            'skip_download': True
        }
    
    def scrape_channel(self, channel_url: str, max_videos: int = 100):
        """
        Extract metadata from all channel videos
        
        Args:
            channel_url: https://www.youtube.com/@ChannelName
            max_videos: limit results
        
        Returns:
            list of video metadata dicts
        """
        logger.info(f"Scraping channel: {channel_url}")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)
        
        videos = []
        
        for entry in channel_info.get('entries', [])[:max_videos]:
            if not entry:
                continue
            
            videos.append({
                'video_id': entry.get('id'),
                'title': entry.get('title'),
                'url': entry.get('url'),
                'duration': entry.get('duration'),
                'view_count': entry.get('view_count'),
                'upload_date': entry.get('upload_date')
            })
        
        logger.info(f"Scraped {len(videos)} videos from channel")
        return videos