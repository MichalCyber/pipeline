"""
Test Fansly download with custom collector
"""

from app.collectors.fansly_collector import FanslyCollector
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

def main():
    print("="*60)
    print("TEST: Fansly Custom Collector")
    print("="*60)
    
    # Check cookies
    cookies_path = Path("cookies/fansly_cookies.txt")
    
    if not cookies_path.exists():
        print("\n❌ Cookies not found!")
        print(f"   Expected: {cookies_path}")
        return
    
    print(f"✅ Cookies found: {cookies_path}")
    
    # Get URL from user
    print("\n📋 Enter Fansly creator profile URL:")
    print("   Example: https://fansly.com/username")
    profile_url = input("URL: ").strip()
    
    if not profile_url:
        profile_url = "https://fansly.com/tootightwithbra"  # Your example
        print(f"Using default: {profile_url}")
    
    # Create collector
    collector = FanslyCollector(cookies_path)
    
    print("\n🔐 Verifying authentication...")
    my_user = collector.check_auth()
    
    if my_user:
        print(f"✅ Authenticated as: @{my_user}")
    else:
        print("❌ Auth failed! Your cookies are either expired or missing the session token.")
        print("   Tip: Log out and log back in on Fansly, then export cookies again.")
        return # Ukončíme test, lebo bez auth to nepôjde
    
    # Download (metadata only first)
    print("\n🔍 Fetching metadata...")
    
    try:
        videos = collector.download_profile(
            profile_url=profile_url,
            max_videos=5,
            output_dir=None  # No download yet
        )
        
        if not videos:
            print("\n⚠️ No videos found. Possible reasons:")
            print("   - Need active subscription to this creator")
            print("   - Expired cookies")
            print("   - Creator has no public videos")
            return
        
        print(f"\n✅ Found {len(videos)} videos")
        
        # Show samples
        for i, v in enumerate(videos[:3], 1):
            print(f"\n{i}. {v['title'][:60] if v['title'] else 'Untitled'}")
            print(f"   Duration: {v['duration']}s")
            print(f"   Resolution: {v['width']}x{v['height']}")
            print(f"   Vertical: {'Yes' if v['is_vertical'] else 'No'}")
        
        # Ask to download
        print("\n" + "="*60)
        download = input("Download these videos? (y/n): ").strip().lower()
        
        if download == 'y':
            output_dir = Path("downloads/fansly_test")
            
            print(f"\n📥 Downloading to: {output_dir}")
            
            videos_downloaded = collector.download_profile(
                profile_url=profile_url,
                max_videos=5,
                output_dir=output_dir
            )
            
            print(f"\n✅ Downloaded {len(videos_downloaded)} videos")
            print(f"📁 Location: {output_dir}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()