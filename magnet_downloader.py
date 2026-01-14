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


class MagnetDownloader:
    """Magnet Downloader class

    Attributes:
        - torrent_url: Nyaa.si torrent page URL
        - arc_folder: Arc folder name

    Methods:
        download() -> None: Download all magnet links
    """

    def __init__(self, torrent_url: str, arc_folder: str):
        self.torrent_url = torrent_url
        self.arc_folder = arc_folder

    def _download_magnets(self, magnets: list[str], arc_folder: str) -> None:
        """
        Download magnets using transmission-cli.

        Args:
            magnets: List of magnet links
            arc_folder: Arc folder name

        """

        # Get correct arc folder name
        # If user provided explicit folder name (contains / or starts with . or arc), use as-is

        print(f"Found {len(magnets)} magnet links")
        print(f"Arc folder: {arc_folder}")

        # Create save directory
        save_path = Path(arc_folder).absolute()
        save_path.mkdir(parents=True, exist_ok=True)

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
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"[{i:2d}/{len(magnets)}] ✗ Error: {e}")
                continue

        print(f"✓ Started {started}/{len(magnets)} downloads in background!")
        print(f"✓ Download folder: {save_path}")

    def _extract_magnets(self, url: str) -> list[str]:
        """
        Extract magnet links from nyaa.si URL.

        Returns:
            List of magnet links, empty list if none found
        """
        EXCLUDED_PATTERNS = [
            "Alternate",  # skip alternate
            "G-8",  # skip fillers
        ]
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

        magnets: list[str] = []

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
                # if "Alternate" not in entry and "G-8" not in entry:
                if not any(pat in entry for pat in EXCLUDED_PATTERNS):
                    magnets.append(magnet)

        # Pattern 2: Single torrent view page (direct magnet links)
        if not magnets:
            direct_magnets = re.findall(r'href=["\']([^"\']*magnet:[^"\']*)["\']', html)
            for magnet in direct_magnets:
                magnet = unescape(magnet)
                magnets.append(magnet)

        # Remove duplicates
        return list(set(magnets))

    def download(self) -> int:
        """Download all magnet links

        Returns:
           Number of magnet links

        """
        print(f"📥 Fetching: {self.torrent_url}")
        magnets = self._extract_magnets(self.torrent_url)

        if not magnets:
            print("❌ No magnet links found on the page", file=sys.stderr)
            raise Exception("No magnet links found on the page")

        print(f"🔍 Extracted {len(magnets)} magnet link(s)")

        self._download_magnets(magnets, self.arc_folder)
        return len(magnets)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(0)

    MagnetDownloader(sys.argv[1], sys.argv[2]).download()
