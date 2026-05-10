"""
Test Fansly profile download with cookies
"""

from app.collectors.profile_downloader import ProfileDownloader
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

def test_fansly_profile():
    """
    Test Fansly creator profile download
    
    NOTE: You need active Fansly subscription + exported cookies
    """
    
    print("="*60)
    print("TEST: Fansly Profile Download")
    print("="*60)
    
    # Check cookies exist
    cookies_path = Path("cookies/fansly_cookies.txt")
    
    if not cookies_path.exists():
        print("\n❌ Cookies not found!")
        print(f"   Expected: {cookies_path}")
        print("\nSteps to fix:")
        print("1. Login to Fansly in browser")
        print("2. Export cookies using browser extension")
        print("3. Save as: cookies/fansly_cookies.txt")
        return
    
    print(f"✅ Cookies found: {cookies_path}")
    
    # Get creator URL from user
    print("\n📋 Enter Fansly creator profile URL:")
    print("   Example: https://fansly.com/tootightwithbra")
    profile_url = input("URL: ").strip()
    
    if not profile_url:
        print("❌ No URL provided")
        return
    
    # Setup downloader
    downloader = ProfileDownloader(
        output_dir=Path("downloads/fansly_test"),
        cookies_file=cookies_path
    )
    
    # Download (start with metadata only for safety)
    print(f"\n🔍 Testing access to: {profile_url}")
    print("   (metadata only - no video download yet)")
    
    try:
        videos = downloader.download_profile(
            profile_url=profile_url,
            max_videos=5,
            download_videos=False  # ✅ Metadata only first
        )
        
        if not videos:
            print("\n⚠️ No videos found. Possible reasons:")
            print("   - Private profile (need subscription)")
            print("   - Expired cookies")
            print("   - Invalid URL")
            return
        
        print(f"\n✅ Access OK! Found {len(videos)} videos")
        
        # Show sample
        for i, v in enumerate(videos[:3], 1):
            print(f"\n{i}. {v['title'][:60]}")
            print(f"   Duration: {v['duration']}s")
            print(f"   Views: {v['views']:,}")
            print(f"   Posted: {v['timestamp']}")
        
        # Ask if want to download
        print("\n" + "="*60)
        print("Do you want to download these videos? (y/n)")
        confirm = input("Download: ").strip().lower()
        
        if confirm == 'y':
            print("\n📥 Downloading videos...")
            
            videos_downloaded = downloader.download_profile(
                profile_url=profile_url,
                max_videos=5,
                download_videos=True  # ✅ Actually download
            )
            
            print(f"\n✅ Downloaded {len(videos_downloaded)} videos")
            print(f"📁 Location: downloads/fansly_test/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fansly_profile()