"""
Test Cookie Rotation System
"""

from src.tools.downloader import VideoDownloader
from src.tools.cookie_manager import get_cookie_manager
import time


def test_cookie_manager():
    """Test cookie manager functionality"""
    print("=" * 60)
    print("TESTING COOKIE ROTATION SYSTEM")
    print("=" * 60)
    
    # Get cookie manager
    manager = get_cookie_manager()
    
    # Show initial stats
    stats = manager.get_stats()
    print(f"\n📊 Cookie Pool Stats:")
    print(f"   Total cookies: {stats['total_cookies']}")
    print(f"   Available: {stats['available']}")
    print(f"   Blocked: {stats['blocked']}")
    
    if stats['total_cookies'] == 0:
        print("\n⚠️  No cookies found!")
        print("📝 Please add cookie files to cookies/ directory")
        print("   See cookies/README.md for instructions")
        return
    
    print(f"\n✅ Found {stats['total_cookies']} cookie files:")
    for cookie_info in stats['cookies']:
        print(f"   - {cookie_info['name']}")
    
    print("\n" + "=" * 60)
    print("TESTING DOWNLOAD WITH COOKIE ROTATION")
    print("=" * 60)
    
    # Test download
    downloader = VideoDownloader(output_dir="test_downloads")
    
    # Test with a short video
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video (18 seconds)
    
    print(f"\n📥 Testing download: {test_url}")
    print("   This will test cookie rotation and retry logic...")
    
    result = downloader.download(test_url)
    
    if result:
        print(f"\n✅ SUCCESS! Downloaded to: {result}")
    else:
        print(f"\n❌ FAILED! Check logs above for errors")
    
    # Show final stats
    print("\n" + "=" * 60)
    print("FINAL STATS")
    print("=" * 60)
    
    stats = downloader.get_stats()
    print(f"\n📊 Cookie Pool Performance:")
    print(f"   Total downloads: {stats['total_downloads']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Available cookies: {stats['available']}/{stats['total_cookies']}")
    
    print(f"\n📋 Individual Cookie Stats:")
    for cookie_info in stats['cookies']:
        status = "🚫 BLOCKED" if cookie_info['is_blocked'] else "✅ Active"
        print(f"   {status} {cookie_info['name']}")
        print(f"      Downloads: {cookie_info['downloads']}")
        print(f"      Success rate: {cookie_info['success_rate']:.1%}")


def test_concurrent_downloads():
    """Test concurrent downloads with cookie rotation"""
    print("\n" + "=" * 60)
    print("TESTING CONCURRENT DOWNLOADS")
    print("=" * 60)
    
    import threading
    
    downloader = VideoDownloader(output_dir="test_downloads")
    
    # Test URLs (short videos)
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # 18s
        "https://www.youtube.com/watch?v=OPf0YbXqDm0",  # 1min
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # 4min
    ]
    
    results = []
    
    def download_worker(url, index):
        print(f"\n🔄 Thread {index}: Starting download...")
        result = downloader.download(url)
        results.append((index, result))
        print(f"{'✅' if result else '❌'} Thread {index}: {'Success' if result else 'Failed'}")
    
    # Start threads
    threads = []
    for i, url in enumerate(test_urls):
        thread = threading.Thread(target=download_worker, args=(url, i+1))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Stagger starts slightly
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # Show results
    print("\n" + "=" * 60)
    print("CONCURRENT DOWNLOAD RESULTS")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    print(f"\n✅ Successful: {success_count}/{len(results)}")
    
    stats = downloader.get_stats()
    print(f"📊 Overall success rate: {stats['success_rate']:.1%}")


if __name__ == "__main__":
    # Test basic functionality
    test_cookie_manager()
    
    # Uncomment to test concurrent downloads
    # test_concurrent_downloads()
