from app.collectors.channel_scraper import ChannelScraper
import json
from pathlib import Path

def main():
    channel_url = "https://www.youtube.com/@honey-drop-dramas"
    max_videos = 50

    scraper = ChannelScraper()
    videos = scraper.scrape_channel(channel_url, max_videos=max_videos)

    print(f"\n Scraped {len(videos)} videos\n")

    # Pretty print first 3
    for v in videos[:3]:
        print(json.dumps(v, indent=2))

    # Optional: save to file for inspection
    out = Path("outputs/debug")
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "channel_videos.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    print(f"\n Saved to outputs/debug/channel_videos.json")

if __name__ == "__main__":
    main()
