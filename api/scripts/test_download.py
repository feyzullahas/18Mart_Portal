"""
Test script to verify the bus schedule downloader functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from download_bus_schedules import (
    fetch_page_content,
    extract_pdf_links,
    check_if_pdf_changed,
    BASE_URL,
    DOWNLOAD_DIR
)

def test_fetch_page():
    """Test fetching the page content"""
    print("=" * 60)
    print("TEST 1: Fetching page content")
    print("=" * 60)
    try:
        html = fetch_page_content(BASE_URL)
        print(f"✓ Successfully fetched {len(html)} bytes of HTML")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        return False

def test_extract_links():
    """Test extracting PDF links"""
    print("\n" + "=" * 60)
    print("TEST 2: Extracting PDF links")
    print("=" * 60)
    try:
        html = fetch_page_content(BASE_URL)
        links = extract_pdf_links(html)
        
        print(f"\nFound {len(links.get('all_weekday', []))} weekday schedule(s):")
        for link in links.get('all_weekday', []):
            print(f"  - {link['text'][:60]}")
            print(f"    {link['href']}")
        
        print(f"\nFound {len(links.get('all_weekend', []))} weekend schedule(s):")
        for link in links.get('all_weekend', []):
            print(f"  - {link['text'][:60]}")
            print(f"    {link['href']}")
        
        print(f"\nSelected weekday: {links.get('weekday', 'None')}")
        print(f"Selected weekend: {links.get('weekend', 'None')}")
        
        if links.get('weekday') and links.get('weekend'):
            print("\n✓ Successfully extracted both schedule types")
            return True
        else:
            print("\n✗ Missing one or both schedule types")
            return False
            
    except Exception as e:
        print(f"✗ Failed to extract links: {e}")
        return False

def test_change_detection():
    """Test change detection functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: Change detection")
    print("=" * 60)
    try:
        html = fetch_page_content(BASE_URL)
        links = extract_pdf_links(html)
        
        if not links.get('weekday'):
            print("✗ No weekday schedule found, skipping test")
            return False
        
        # Test with existing file
        weekday_url = links['weekday']
        has_changed, remote_size = check_if_pdf_changed(weekday_url, "weekday_schedule.pdf")
        
        print(f"\nWeekday schedule URL: {weekday_url}")
        print(f"Remote file size: {remote_size:,} bytes")
        print(f"Has changed: {has_changed}")
        
        local_file = DOWNLOAD_DIR / "weekday_schedule.pdf"
        if local_file.exists():
            local_size = local_file.stat().st_size
            print(f"Local file size: {local_size:,} bytes")
            
            if local_size == remote_size:
                print("\n✓ Change detection working correctly (sizes match)")
            else:
                print("\n⚠ File sizes differ - will download new version")
        else:
            print("\n⚠ Local file doesn't exist - will download")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed change detection test: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BUS SCHEDULE DOWNLOADER - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Fetch Page", test_fetch_page()))
    results.append(("Extract Links", test_extract_links()))
    results.append(("Change Detection", test_change_detection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total_tests - total_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
