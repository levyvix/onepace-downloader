"""Download One Pace subtitles from Google Drive.

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

import subprocess
import sys
from pathlib import Path


class SubtitleDownloader:
    def __init__(self, gdrive_url: str, arc_folder: str) -> None:
        self.gdrive_url = gdrive_url
        self.arc_folder = arc_folder

    def download(self):
        arc_path = Path(self.arc_folder)
        if not arc_path.exists():
            arc_path.mkdir(parents=True, exist_ok=True)

        subtitles_folder = arc_path / "subtitles"
        subtitles_folder.mkdir(exist_ok=True, parents=True)
        print(f"Downloading subtitles to: {subtitles_folder}")
        print(f"From: {self.gdrive_url}")
        try:
            subprocess.run(
                [
                    "gdown",
                    "--folder",
                    "-O",
                    str(subtitles_folder),
                    self.gdrive_url,
                    "--remaining-ok",
                ],
                check=True,
                # shell=True,
            )
            print()
            print("=" * 70)
            print("✓ Download complete!")
            print(f"✓ Subtitles saved to: {subtitles_folder}")
            print()
            print("Next steps:")
            print(f"  1. Verify files: ls -1 '{subtitles_folder}'")
            print(
                f"  2. Match subtitles: python3 match_onepace_subtitles.py '{self.arc_folder}' '{subtitles_folder}'"
            )
            print("=" * 70)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading from Google Drive: {e}")
            return 1
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    SubtitleDownloader(sys.argv[0], sys.argv[1]).download()
