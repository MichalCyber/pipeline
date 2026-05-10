from yt_dlp import YoutubeDL
from pathlib import Path
import json

DOWNLOAD_DIR = Path("downloads")
META_FILE = DOWNLOAD_DIR / "videos.json"


def load_existing_videos():
    if META_FILE.exists():
        return json.loads(META_FILE.read_text(encoding="utf-8"))
    return {}


def save_metadata(data):
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    META_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def extract_videos(page_url, max_videos=50):
    ydl_opts = {
        "quiet": False,
        "extract_flat": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(page_url, download=False)

    videos = []

    for e in info.get("entries", [])[:max_videos]:
        if not e:
            continue

        videos.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
            "duration": e.get("duration"),
            "view_count": e.get("view_count"),
        })

    print(f"🔍 Found {len(videos)} videos")
    return videos


def download_videos(videos):
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    existing = load_existing_videos()

    to_download = []
    metadata = existing.copy()

    for v in videos:
        vid = v["id"]
        if not vid:
            continue

        output_file = DOWNLOAD_DIR / f"{vid}.mp4"

        if output_file.exists():
            print(f"⏭️  Skipping (already exists): {vid}")
        else:
            to_download.append(v["url"])

        metadata[vid] = {
            **v,
            "downloaded_video": str(output_file)
        }

    if to_download:
        ydl_opts = {
            "outtmpl": str(DOWNLOAD_DIR / "%(title).80s.%(ext)s"),
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(to_download)

    save_metadata(metadata)
    print(f"📄 Metadata saved to {META_FILE}")


if __name__ == "__main__":
    PAGE_URL = "https://www.youtube.com/@ShortDrama-French666/videos"
    # PAGE_URL = "https://www.dailymotion.com/Fast.Cut"  # ← funguje tiež

    MAX_VIDEOS = 5

    videos = extract_videos(PAGE_URL, MAX_VIDEOS)
    download_videos(videos)
