import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.collectors.profile_downloader import ProfileDownloader
from pathlib import Path
'''
downloader = ProfileDownloader(
    output_dir=Path("downloads/youtube_channel"),
    cookies_file=Path("cookies/youtube_cookies.txt")  # YouTube doesn't need cookies
)

# Download z YouTube kanála
videos = downloader.download_profile(
    profile_url="https://www.youtube.com/@NaNaDramaNO1",
    max_videos=10,
    download_videos=True  # ✅ Stiahne skutočné videá
)
'''
downloader = ProfileDownloader(
    output_dir=Path("downloads/fansly"),
   # cookies_file=Path("cookies/fansly_cookies.txt")  # Optional
)

videos = downloader.download_profile(
    profile_url="https://fansly.com/tootightwithbra/posts",  # Example
    max_videos=20,
    download_videos=True
)
'''
downloader = ProfileDownloader(
    output_dir=Path("downloads/facebook_page"),
    cookies_file=Path("cookies/facebook_cookies.txt")  # ✅ REQUIRED
)

videos = downloader.download_profile(
    profile_url="https://www.facebook.com/SomePageName",
    max_videos=15,
    download_videos=True
)

downloader = ProfileDownloader(
    output_dir=Path("downloads/instagram_profile"),
    cookies_file=Path("cookies/instagram_cookies.txt")  # ✅ REQUIRED
)

videos = downloader.download_profile(
    profile_url="https://www.instagram.com/username/",
    max_videos=25,
    download_videos=True
)
'''
print(f"Downloaded {len(videos)} videos")
for v in videos:
    print(f"- {v['title']} ({v['duration']}s)")
