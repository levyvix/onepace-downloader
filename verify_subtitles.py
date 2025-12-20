#!/usr/bin/env python3
"""
Verify that all video files have matching subtitle files.

Usage:
    python3 verify_subtitles.py <directory>

Example:
    python3 verify_subtitles.py "arc11-drum_island"
    python3 verify_subtitles.py "arc10-little_garden/[One Pace][115-129] Little Garden [480p]"
"""
import sys
from pathlib import Path


def verify_subtitles(directory):
    """Check if all .mkv files have matching .ass files."""
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Error: Directory not found: {directory}")
        return False

    # Get all video files
    videos = sorted(dir_path.glob("*.mkv"))

    if not videos:
        print(f"No .mkv files found in: {directory}")
        return False

    print(f"Checking {len(videos)} video files in: {directory}")
    print("="*70)

    all_matched = True
    matched_count = 0

    for video in videos:
        subtitle = video.with_suffix('.ass')
        exists = subtitle.exists()

        status = "✓" if exists else "✗"
        print(f"{status} {video.name}")

        if exists:
            print(f"  → {subtitle.name}")
            matched_count += 1
        else:
            print(f"  → MISSING: {subtitle.name}")
            all_matched = False

        print()

    print("="*70)
    print(f"Result: {matched_count}/{len(videos)} videos have matching subtitles")

    if all_matched:
        print("✓ All videos have matching subtitle files!")
        return True
    else:
        print("✗ Some videos are missing subtitle files")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 verify_subtitles.py <directory>")
        print("\nExample:")
        print('  python3 verify_subtitles.py "arc11-drum_island"')
        print('  python3 verify_subtitles.py "arc10-little_garden/[One Pace][115-129] Little Garden [480p]"')
        sys.exit(1)

    directory = sys.argv[1]
    success = verify_subtitles(directory)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
