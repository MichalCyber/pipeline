import requests
from pathlib import Path
from typing import Optional
import json
import logging
import time
from http.cookiejar import MozillaCookieJar

logger = logging.getLogger(__name__)


class FanslyCollector:
    API_BASE = "https://apiv3.fansly.com/api/v1"
    
    def __init__(self, cookies_file: Path):
        self.cookies_file = cookies_file
        self.session = requests.Session()
        self._load_cookies()
    def _load_cookies(self):
        logger.info(f"Loading cookies from: {self.cookies_file}")
        try:
            jar = MozillaCookieJar(str(self.cookies_file))
            jar.load(ignore_discard=True, ignore_expires=True)
            self.session.cookies = jar
            
            auth_token = None
            for cookie in jar:
                # Priorita pre f-s-c (Firefox) alebo session_active_session
                if cookie.name in ['f-s-c', 'session_active_session']:
                    auth_token = cookie.value
                    break
            
            if auth_token:
                self.session.headers.update({
                    'Authorization': auth_token,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'x-requested-with': 'XMLHttpRequest', # Dôležité pre Fansly API
                    'Origin': 'https://fansly.com',
                    'Referer': 'https://fansly.com/'
                })
                logger.info("✅ Auth token (f-s-c) bol úspešne priradený.")
            else:
                logger.warning("⚠️ V cookies.txt sa nenašiel f-s-c ani session_active_session!")
                
        except Exception as e:
            logger.error(f"Nepodarilo sa načítať cookies: {e}")

    def check_auth(self) -> Optional[str]:
        """Overí, či sú cookies platné a vráti tvoje používateľské meno"""
        url = f"{self.API_BASE}/account/me" # Upravená URL pre verifikáciu
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success'):
                    return data['response'].get('username')
            return None
        except Exception:
            return None
        
    def download_profile(
        self,
        profile_url: str,
        max_videos: int = 50,
        output_dir: Optional[Path] = None
    ) -> list[dict]:
        """
        Download videos from Fansly creator profile
        
        Args:
            profile_url: Full profile URL (e.g., https://fansly.com/username)
            max_videos: Maximum videos to download
            output_dir: Where to save videos (optional)
        
        Returns:
            List of video metadata dicts
        """
        
        # Extract username from URL
        username = profile_url.rstrip('/').split('/')[-1]
        logger.info(f"Downloading from @{username}...")
        
        # 1. Get account info
        account_id = self._get_account_id(username)
        if not account_id:
            logger.error(f"Account not found: {username}")
            return []
        
        logger.info(f"Found account ID: {account_id}")
        
        # 2. Get timeline posts
        posts = self._get_timeline(account_id, max_videos)
        logger.info(f"Found {len(posts)} posts with media")
        
        # 3. Extract video metadata
        videos = []
        for post in posts:
            video_meta = self._extract_video_metadata(post)
            if video_meta:
                videos.append(video_meta)
        
        logger.info(f"Extracted {len(videos)} videos")
        
        # 4. Download videos if output_dir specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for i, video in enumerate(videos, 1):
                logger.info(f"[{i}/{len(videos)}] Downloading: {video['video_id']}")
                
                success = self._download_video(
                    video_url=video['download_url'],
                    output_path=output_dir / f"{video['video_id']}.mp4"
                )
                
                if success:
                    video['local_path'] = str(output_dir / f"{video['video_id']}.mp4")
                    
                    # Save metadata
                    meta_path = output_dir / f"{video['video_id']}_meta.json"
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(video, f, indent=2, ensure_ascii=False)
                
                time.sleep(1)  # Rate limiting
        
        return videos
    
    def _get_account_id(self, username: str) -> Optional[str]:
        """Získa ID účtu podľa mena"""
        url = f"{self.API_BASE}/account"
        params = {'usernames': username}
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            
            # DEBUG INFO - teraz je to na správnom mieste
            logger.debug(f"DEBUG: Status Code: {resp.status_code}")
            
            resp.raise_for_status()
            data = resp.json()
            
            if data.get('success') and data.get('response'):
                accounts = data['response']
                if accounts:
                    return accounts[0]['id']
            
        except Exception as e:
            logger.error(f"Nepodarilo sa získať account ID pre {username}: {e}")
        
        return None
    
    def _get_timeline(self, account_id: str, max_posts: int) -> list[dict]:
        """Fetch posts from account timeline"""
        
        url = f"{self.API_BASE}/timeline/{account_id}"
        params = {
            'before': 0,
            'after': 0,
            'wallId': '',
            'contentSearch': '',
            'ngsw-bypass': 'true'
        }
        
        posts = []
        
        try:
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            
            data = resp.json()
            
            if data.get('success') and data.get('response'):
                timeline_posts = data['response'].get('posts', [])
                
                # Filter posts with video attachments
                for post in timeline_posts:
                    attachments = post.get('attachments', [])
                    
                    has_video = any(
                        att.get('contentType') == 2  # 2 = video
                        for att in attachments
                    )
                    
                    if has_video:
                        posts.append(post)
                        
                        if len(posts) >= max_posts:
                            break
            
        except Exception as e:
            logger.error(f"Failed to fetch timeline: {e}")
        
        return posts
    
    def _extract_video_metadata(self, post: dict) -> Optional[dict]:
        """Extract video metadata from post"""
        
        attachments = post.get('attachments', [])
        
        for attachment in attachments:
            if attachment.get('contentType') == 2:  # Video
                
                # Get video URL (highest quality)
                locations = attachment.get('locations', [])
                video_url = None
                
                if locations:
                    # Sort by quality
                    locations.sort(key=lambda x: x.get('width', 0), reverse=True)
                    video_url = locations[0].get('location')
                
                if not video_url:
                    continue
                
                return {
                    'platform': 'fansly',
                    'video_id': str(post.get('id', '')),
                    'post_id': str(post.get('id', '')),
                    'url': f"https://fansly.com/post/{post.get('id', '')}",
                    'download_url': video_url,
                    'title': post.get('content', '')[:100],
                    'caption': post.get('content', ''),
                    'description': post.get('content', ''),
                    'duration': attachment.get('duration', 0),
                    'width': attachment.get('width', 0),
                    'height': attachment.get('height', 0),
                    'timestamp': post.get('createdAt', 0) / 1000,  # ms to seconds
                    'is_vertical': attachment.get('height', 0) > attachment.get('width', 0),
                    'author': post.get('account', {}).get('username', ''),
                    'views': 0,  # Fansly doesn't expose view count publicly
                    'likes': 0,  # Same with likes
                    'raw': post
                }
        
        return None
    
    def _download_video(self, video_url: str, output_path: Path) -> bool:
        """Download video file"""
        
        try:
            resp = self.session.get(video_url, stream=True, timeout=30)
            resp.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"✅ Downloaded: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False