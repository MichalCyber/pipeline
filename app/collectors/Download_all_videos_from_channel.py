from yt_dlp import YoutubeDL

def extract_video_urls(page_url, max_videos=50):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(page_url, download=False)

    urls = []
    if "entries" in info:
        for e in info["entries"][:max_videos]:
            if e and "url" in e:
                urls.append("https://www.youtube.com/watch?v=" + e["id"])
    return urls

def download_videos(urls):
    ydl_opts = {
        "outtmpl": "downloads/%(title).80s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

