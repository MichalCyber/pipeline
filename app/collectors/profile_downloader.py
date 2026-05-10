import yt_dlp
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


class ProfileDownloader:
    """
    Download all videos from social media profile
    
    Supported:
    - YouTube channels
    - TikTok profiles
    - Instagram profiles (requires cookies)
    - Facebook pages (requires cookies)
    - Dailymotion users
    """
    
    def __init__(self, output_dir: Path, cookies_file: Optional[Path] = None):
        """
        Args:
            output_dir: Where to save videos
            cookies_file: Browser cookies for auth
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
            'format': 'best',
            'cookiefile': str(cookies_file) if cookies_file else None,
            'writeinfojson': True,  # Save metadata JSON
            'writethumbnail': True,  # Save thumbnails
        }
    
    def download_profile(
        self,
        profile_url: str,
        max_videos: int = 50,
        download_videos: bool = True
    ) -> list[dict]:
        """
        Download videos from profile URL
        
        Args:
            profile_url: Full profile URL (e.g., https://www.tiktok.com/@username)
            max_videos: Maximum videos to download
            download_videos: If False, only extract metadata
        
        Returns:
            List of video metadata dicts
        
        Examples:
            # YouTube channel
            download_profile('https://www.youtube.com/@ChannelName')
            
            # TikTok profile
            download_profile('https://www.tiktok.com/@username')
            
            # Instagram profile
            download_profile('https://www.instagram.com/username/')
            
            # Facebook page
            download_profile('https://www.facebook.com/PageName')
            
            # Dailymotion user
            download_profile('https://www.dailymotion.com/username')
        """
        
        logger.info(f"Downloading from: {profile_url}")
        logger.info(f"Max videos: {max_videos}")
        
        # Update options
        opts = self.ydl_opts.copy()
        
        if not download_videos:
            opts['skip_download'] = True
            logger.info("Metadata-only mode (no video download)")
        
        # Platform-specific handling
        platform = self._detect_platform(profile_url)
        logger.info(f"Detected platform: {platform}")
        
        videos = []
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract info
                logger.info("Extracting profile info...")
                result = ydl.extract_info(profile_url, download=False)
                
                if not result:
                    logger.error("Failed to extract profile info")
                    return []
                
                # Handle playlist/channel
                if 'entries' in result:
                    entries = list(result['entries'])[:max_videos]
                    logger.info(f"Found {len(entries)} videos")
                    
                    # Download each video
                    for i, entry in enumerate(entries, 1):
                        if not entry:
                            continue
                        
                        video_url = entry.get('webpage_url') or entry.get('url')
                        if not video_url:
                            continue
                        
                        logger.info(f"[{i}/{len(entries)}] Processing: {video_url}")
                        
                        try:
                            if download_videos:
                                info = ydl.extract_info(video_url, download=True)
                            else:
                                info = entry
                            
                            # Save metadata
                            video_meta = self._extract_metadata(info, platform)
                            videos.append(video_meta)
                            
                            # Save JSON
                            self._save_metadata(video_meta)
                            
                        except Exception as e:
                            logger.warning(f"Failed to process video: {e}")
                            continue
                
                else:
                    # Single video
                    logger.info("Single video detected")
                    if download_videos:
                        ydl.download([profile_url])
                    
                    video_meta = self._extract_metadata(result, platform)
                    videos.append(video_meta)
                    self._save_metadata(video_meta)
        
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return []
        
        logger.info(f"✅ Downloaded {len(videos)} videos")
        
        return videos
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower or 'fb.com' in url_lower:
            return 'facebook'
        elif 'dailymotion.com' in url_lower:
            return 'dailymotion'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'reddit.com' in url_lower:
            return 'reddit'
        else:
            return 'unknown'
    
    def _extract_metadata(self, info: dict, platform: str) -> dict:
        """Extract relevant metadata from yt-dlp info"""
        
        return {
            'platform': platform,
            'video_id': info.get('id', ''),
            'url': info.get('webpage_url', ''),
            'title': info.get('title', ''),
            'description': info.get('description', ''),
            'duration': info.get('duration'),
            'views': info.get('view_count', 0) or 0,
            'likes': info.get('like_count', 0) or 0,
            'timestamp': info.get('timestamp', 0),
            'uploader': info.get('uploader', ''),
            'uploader_url': info.get('uploader_url', ''),
            'thumbnail': info.get('thumbnail', ''),
            'width': info.get('width', 0),
            'height': info.get('height', 0),
            'fps': info.get('fps', 0),
            'format': info.get('format', ''),
            'filesize': info.get('filesize', 0),
            'filename': f"{info.get('id', 'unknown')}.{info.get('ext', 'mp4')}",
        }
    
    def _save_metadata(self, meta: dict):
        """Save metadata to JSON file"""
        
        json_path = self.output_dir / f"{meta['video_id']}_meta.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved metadata: {json_path.name}")
    
    def get_downloaded_videos(self) -> list[dict]:
        """
        Get list of all downloaded videos with metadata
        
        Returns:
            List of video metadata dicts
        """
        
        videos = []
        
        for json_file in self.output_dir.glob('*_meta.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    videos.append(meta)
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
        
        return videos