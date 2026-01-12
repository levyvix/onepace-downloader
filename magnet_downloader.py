#!/usr/bin/env python3
"""
Extract magnet links from nyaa.si and download with transmission-cli (all in one command).

Usage:
    uv run magnet_downloader.py <nyaa.si_url> <folder_name>

Examples:
    # Use exact folder name (starts with "arc")
    uv run magnet_downloader.py \
      "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
      "arc15-jaya"

    # Auto-prefixes with "arc-" (doesn't start with "arc")
    uv run magnet_downloader.py \
      "https://nyaa.si/?f=0&c=0_0&q=one+pace+water+seven" \
      "water_seven"
    # Creates: arc-water_seven/

    # Explicit path always used as-is
    uv run magnet_downloader.py \
      "https://nyaa.si/view/608554" \
      "./my-custom-folder"

Folder naming rules:
  - Starts with "arc": used exactly as-is
  - Contains "/": used exactly as-is (explicit path)
  - Otherwise: auto-prefixes with "arc-" and normalizes

The script:
  1. Fetches the nyaa.si page
  2. Extracts all magnet links
  3. Creates the folder
  4. Starts all downloads asynchronously with transmission-cli
  5. Returns immediately (downloads continue in background)
"""

import subprocess
import re
import sys
from pathlib import Path
from html import unescape

# Try to import arc_mapping for auto-detection
try:
    from arc_mapping import get_arc_folder_name
except ImportError:
    def get_arc_folder_name(arc_name: str) -> str:
        """Fallback if arc_mapping not available"""
        return f"arc-{arc_name.lower().replace(' ', '_')}"


def extract_magnets(url: str) -> list:
    """
    Extract magnet links from nyaa.si URL.

    Returns:
        List of magnet links, empty list if none found
    """
    try:
        result = subprocess.run(
            ["curl", "-s", url, "--compressed"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return []

        html = result.stdout
        if not html:
            return []

    except Exception:
        return []

    magnets = []

    # Pattern 1: Search results page (table rows)
    entries = re.findall(
        r'<tr[^>]*>.*?(<a[^>]*href=["\']magnet:[^"\']*["\'][^>]*>.*?</a>).*?</tr>',
        html,
        re.DOTALL,
    )

    for entry in entries:
        magnet_match = re.search(r'href=["\']([^"\']*magnet:[^"\']*)["\']', entry)
        if magnet_match:
            magnet = unescape(magnet_match.group(1))
            if "Alternate" not in entry and "G-8" not in entry:
                magnets.append(magnet)

    # Pattern 2: Single torrent view page (direct magnet links)
    if not magnets:
        direct_magnets = re.findall(
            r'href=["\']([^"\']*magnet:[^"\']*)["\']', html
        )
        for magnet in direct_magnets:
            magnet = unescape(magnet)
            magnets.append(magnet)

    # Remove duplicates
    return list(set(magnets))


def download_magnets(magnets: list, arc_name: str) -> int:
    """
    Download magnets using transmission-cli.

    Args:
        magnets: List of magnet links
        arc_name: Arc name or folder name

    Returns:
        0 on success, 1 on error
    """
    if not magnets:
        print("❌ No magnet links to download", file=sys.stderr)
        return 1

    # Get correct arc folder name
    # If user provided explicit folder name (contains / or starts with . or arc), use as-is
    if '/' in arc_name or arc_name.startswith('.') or arc_name.lower().startswith('arc'):
        arc_folder = arc_name
    else:
        try:
            arc_folder = get_arc_folder_name(arc_name)
        except (ValueError, NameError):
            # Fallback if arc_mapping fails
            arc_folder = f"arc-{arc_name.lower().replace(' ', '_')}"

    print("=" * 70)
    print(f"Magnet Downloader - {arc_name}")
    print("=" * 70)
    print(f"Found {len(magnets)} magnet links")
    print(f"Arc folder: {arc_folder}")
    print()

    # Create save directory
    save_path = Path(arc_folder).absolute()
    try:
        save_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating folder: {e}", file=sys.stderr)
        return 1

    # Start all downloads asynchronously (non-blocking)
    started = 0
    for i, magnet in enumerate(magnets, 1):
        try:
            # Start transmission-cli in background (non-blocking)
            subprocess.Popen(
                ["transmission-cli", "-w", str(save_path), magnet],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[{i:2d}/{len(magnets)}] ✓ Started", end="\r")
            started += 1
        except Exception as e:
            print(f"[{i:2d}/{len(magnets)}] ✗ Error: {e}")

    print()
    print("=" * 70)
    print(f"✓ Started {started}/{len(magnets)} downloads in background!")
    print(f"✓ Download folder: {save_path}")
    print("=" * 70)
    print("\nDownloads are running in background. You can:")
    print("  1. Monitor progress: transmission-remote -l")
    print("  2. Download subtitles in parallel")
    print("  3. Check back later")
    print()

    return 0 if started > 0 else 1


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    arc_name = sys.argv[2]

    print(f"📥 Fetching: {url}")
    magnets = extract_magnets(url)

    if not magnets:
        print("❌ No magnet links found on the page", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Extracted {len(magnets)} magnet link(s)")
    print()

    sys.exit(download_magnets(magnets, arc_name))


if __name__ == "__main__":
    main()
