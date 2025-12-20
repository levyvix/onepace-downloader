#!/usr/bin/env python3
"""
Download One Pace subtitles from Google Drive.

Usage:
    uv run --with gdown download_subtitles.py <google_drive_url> <arc_name_or_folder>

Examples:
    # Auto-detect arc number from name
    uv run --with gdown download_subtitles.py \
        "https://drive.google.com/drive/folders/..." \
        "jaya"  # Creates arc15-jaya

    # Or use explicit arc folder name
    uv run --with gdown download_subtitles.py \
        "https://drive.google.com/drive/folders/..." \
        "arc15-jaya"

    # Or use custom path
    uv run --with gdown download_subtitles.py \
        "https://drive.google.com/drive/folders/..." \
        "arc10-little_garden/[One Pace][115-129] Little Garden [480p]"
"""

import sys
import subprocess
from pathlib import Path


def get_arc_folder_name(name):
    return name


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    gdrive_url = sys.argv[1]
    arc_input = sys.argv[2]

    # Auto-detect arc folder name (e.g., "jaya" → "arc15-jaya")
    try:
        arc_folder = get_arc_folder_name(arc_input)
        if arc_folder != arc_input:
            print(f"Auto-detected: '{arc_input}' → '{arc_folder}'")
    except ValueError as e:
        # If auto-detection fails, use input as-is
        print(f"Warning: {e}")
        print(f"Using folder name as provided: {arc_input}")
        arc_folder = arc_input

    # Ensure arc folder exists
    arc_path = Path(arc_folder)
    arc_path.mkdir(parents=True, exist_ok=True)

    # Create subtitles subfolder
    subtitles_folder = arc_path / "subtitles"
    subtitles_folder.mkdir(exist_ok=True)

    print(f"Downloading subtitles to: {subtitles_folder}")
    print(f"From: {gdrive_url}")
    print()

    # Use gdown to download the folder
    try:
        subprocess.run(
            [
                "gdown",
                "--folder",
                gdrive_url,
                "-O",
                str(subtitles_folder),
                "--remaining-ok",
            ],
            check=True,
        )
        print()
        print("=" * 70)
        print("✓ Download complete!")
        print(f"✓ Subtitles saved to: {subtitles_folder}")
        print()
        print("Next steps:")
        print(f"  1. Verify files: ls -1 '{subtitles_folder}'")
        print(
            f"  2. Match subtitles: python3 match_onepace_subtitles.py '{arc_folder}' '{subtitles_folder}'"
        )
        print("=" * 70)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading from Google Drive: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
