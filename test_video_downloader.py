from yt_dlp import YoutubeDL
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")


def extract_video_urls(page_url, max_videos=50):
    ydl_opts = {
        "quiet": False,
        "extract_flat": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(page_url, download=False)

    urls = []

    if "entries" in info:
        for e in info["entries"][:max_videos]:
            if not e:
                continue

            video_id = e.get("id")
            if video_id:
                urls.append(f"https://www.youtube.com/watch?v={video_id}")

    print(f"🔍 Found {len(urls)} video URLs")
    return urls


def download_videos(urls):
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    ydl_opts = {
        "outtmpl": str(DOWNLOAD_DIR / "%(title).80s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    PAGE_URL = "https://www.youtube.com/@Honey-Drop-Dramas"  # ← zmeň na test
    MAX_VIDEOS = 3  

    urls = extract_video_urls(PAGE_URL, MAX_VIDEOS)

    for u in urls:
        print("➡️", u)

    if urls:
        download_videos(urls)
