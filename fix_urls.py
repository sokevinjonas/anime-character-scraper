#!/usr/bin/env python3
"""
Script to fix malformed URLs in characters.json and levels.json
Fixes issues like double slashes, incorrect domain concatenation, etc.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

def clean_url(url):
    """Clean and fix malformed URLs"""
    if not url or url == "null":
        return None

    if not isinstance(url, str):
        return None

    url = url.strip()

    if not url:
        return None

    # Fix: https://fr.wikipedia.org//upload.wikimedia.org/...
    # Should be: https://upload.wikimedia.org/...
    if "fr.wikipedia.org//" in url:
        url = url.replace("fr.wikipedia.org//", "")

    # Fix: https://en.wikipedia.org//upload.wikimedia.org/...
    if "en.wikipedia.org//" in url:
        url = url.replace("en.wikipedia.org//", "")

    # Fix: Remove double slashes except after protocol (://)
    # Replace /// or more with just /
    url = re.sub(r'(?<!:)//+', '/', url)

    # Ensure proper protocol
    if url.startswith('http:/') and not url.startswith('http://'):
        url = 'http://' + url[7:]
    elif url.startswith('https:/') and not url.startswith('https://'):
        url = 'https://' + url[8:]

    # Validate URL structure
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            return None
    except:
        return None

    return url if url.startswith('http') else None

def fix_json_file(filepath, json_key=None):
    """Fix URLs in a JSON file"""
    print(f"\nReading {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixes = 0
    broken = 0

    if json_key and json_key in data:
        items = data[json_key]
    else:
        items = data if isinstance(data, list) else []

    for item in items:
        if not isinstance(item, dict):
            continue

        # Check imageUrl field
        if 'imageUrl' in item:
            original = item['imageUrl']
            cleaned = clean_url(original)

            if original != cleaned:
                if cleaned:
                    print(f"  ✓ Fixed: {original[:60]}... → {cleaned[:60]}...")
                    item['imageUrl'] = cleaned
                else:
                    print(f"  ✗ Removed broken URL: {original[:60]}...")
                    item['imageUrl'] = None
                fixes += 1

        # Check nested attributes for image URLs (in levels)
        if 'attributes' in item and isinstance(item['attributes'], dict):
            if 'imageUrl' in item['attributes']:
                original = item['attributes']['imageUrl']
                cleaned = clean_url(original)

                if original != cleaned:
                    if cleaned:
                        print(f"  ✓ Fixed (nested): {original[:60]}... → {cleaned[:60]}...")
                        item['attributes']['imageUrl'] = cleaned
                    else:
                        item['attributes']['imageUrl'] = None
                    fixes += 1

    # Save corrected file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Fixed {fixes} URLs in {filepath}")
    return fixes

def main():
    import sys

    base_dir = Path(__file__).parent / "backend_data"

    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])

    files_to_fix = [
        (base_dir / "characters.json", "characters"),
        (base_dir / "levels.json", "levels"),
    ]

    total_fixes = 0
    for filepath, key in files_to_fix:
        if filepath.exists():
            total_fixes += fix_json_file(filepath, key)
        else:
            print(f"⚠️  File not found: {filepath}")

    print(f"\n{'='*60}")
    print(f"✓ Total URL fixes: {total_fixes}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
