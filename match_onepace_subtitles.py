#!/usr/bin/env python3
"""
Match and rename One Pace subtitle files to match video filenames.

Usage:
    python3 match_onepace_subtitles.py <video_dir> <subtitle_dir>

Example:
    uv run  match_onepace_subtitles.py \\
        "arc10-little_garden/[One Pace][115-129] Little Garden [480p]" \\
        "arc10-little_garden/[One Pace][115-129] Little Garden [480p]/drive-download-20251220T150238Z-1-001"

The script will:
1. Find all .mkv video files in the video directory
2. Find all .ass subtitle files in the subtitle directory
3. Match them by episode number
4. Rename subtitles to match video filenames (keeping .ass extension)
"""

import sys
import re
from pathlib import Path


def extract_episode_number(filename, arc_name):
    """
    Extract episode number from filename.

    Handles various patterns:
    - "Arc Name 01.ass" -> "01"
    - "46 - Arc Name 04.ass" -> "04"
    - "[One Pace][123-126] Arc Name 04 [480p][HASH].mkv" -> "04"
    """
    # Try to extract from "Arc Name XX" pattern
    pattern = rf"{re.escape(arc_name)}\s+(\d+)"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return match.group(1)

    # Fallback: just look for any number pattern
    match = re.search(r"(\d{2})", filename)
    if match:
        return match.group(1)

    return None


def guess_arc_name(video_files):
    """
    Guess the arc name from video filenames.

    Expects pattern like: [One Pace][XXX-XXX] Arc Name XX [480p][HASH].mkv
    """
    if not video_files:
        return None

    # Try to extract arc name from first video
    first_video = video_files[0].name
    # Pattern: [One Pace][XXX-XXX] Arc Name XX [480p]
    match = re.search(r"\[One Pace\]\[\d+-\d+\]\s+(.+?)\s+\d+\s+\[", first_video)
    if match:
        return match.group(1).strip()

    return None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    video_dir = Path(sys.argv[1])
    subtitle_dir = Path(sys.argv[2])

    # Validate directories
    if not video_dir.exists():
        print(f"Error: Video directory not found: {video_dir}")
        sys.exit(1)

    if not subtitle_dir.exists():
        print(f"Error: Subtitle directory not found: {subtitle_dir}")
        sys.exit(1)

    # Get all video and subtitle files
    videos = sorted([f for f in video_dir.glob("*.mkv")])
    subtitles = sorted([f for f in subtitle_dir.glob("*.ass")])

    if not videos:
        print(f"Error: No .mkv files found in {video_dir}")
        sys.exit(1)

    if not subtitles:
        print(f"Error: No .ass files found in {subtitle_dir}")
        sys.exit(1)

    print(f"Found {len(videos)} video files:")
    for v in videos:
        print(f"  - {v.name}")

    print(f"\nFound {len(subtitles)} subtitle files:")
    for s in subtitles:
        print(f"  - {s.name}")

    # Guess arc name from videos
    arc_name = guess_arc_name(videos)
    if arc_name:
        print(f"\nDetected arc name: '{arc_name}'")
    else:
        print("\nWarning: Could not detect arc name, using generic matching")

    # Build subtitle map by episode number
    subtitle_map: dict[str, Path] = {}
    for sub in subtitles:
        ep_num = extract_episode_number(sub.name, arc_name or "")
        if ep_num:
            subtitle_map[ep_num] = sub
        else:
            print(f"Warning: Could not extract episode number from: {sub.name}")

    print("\n" + "=" * 70)
    print("Matching and renaming subtitles:")
    print("=" * 70)

    matched_count = 0
    for video in videos:
        ep_num = extract_episode_number(video.name, arc_name or "")
        if ep_num and ep_num in subtitle_map:
            old_sub = subtitle_map[ep_num]
            # Create new subtitle name by replacing .mkv with .ass
            new_sub_name = video.name.replace(".mkv", ".ass")
            new_sub_path = video_dir / new_sub_name

            print(f"\nEpisode {ep_num}:")
            print(f"  Video:    {video.name}")
            print(f"  Old sub:  {old_sub.name}")
            print(f"  New sub:  {new_sub_name}")
            print("Renaming...", end=" ")

            # Rename the file
            try:
                old_sub.rename(new_sub_path)
                print("  ✓ Renamed successfully")
                matched_count += 1
            except Exception as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"\nWarning: No subtitle found for video: {video.name}")

    print("\n" + "=" * 70)
    if matched_count == len(videos):
        print("✓ All videos matched with subtitles!")
    print(
        f"Done! Successfully matched {matched_count}/{len(videos)} videos with subtitles"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
