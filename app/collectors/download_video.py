from yt_dlp import YoutubeDL
from pathlib import Path

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

def download_video(url: str, max_duration: int | None = None):
    ydl_opts = {
        "outtmpl": str(OUTPUT_DIR / "%(title).80s.%(ext)s"),
        "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/mp4",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        duration = info.get("duration", 0)
        if max_duration and duration > max_duration:
            print(f"⏭ Skipping (duration {duration}s > {max_duration}s)")
            return None

        ydl.download([url])
        print("✅ Downloaded:", info.get("title"))

    return info


if __name__ == "__main__":
    download_video(
        "https://www.youtube.com/watch?v=VIDEO_ID",
        max_duration=180  # 3 min limit (Shorts-friendly)
    )
