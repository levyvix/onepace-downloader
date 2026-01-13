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

from re import sub
import subprocess
import sys
from pathlib import Path


class SubtitleDownloader:
    """Download One Pace subtitles from Google Drive."""

    def __init__(self, gdrive_url: str, arc_folder: str) -> None:
        self.gdrive_url = gdrive_url
        self.arc_folder = arc_folder

    def _setup_path(self):
        """Setup arc path object and create folder if not exists"""
        arc_path = None
        arc_path = Path(self.arc_folder)
        if not arc_path.exists():
            arc_path.mkdir(parents=True, exist_ok=True)
        return arc_path

    def _setup_subtitle_folder(self, arc_path: Path):
        """Setup subtiles/ folder inside arc path, and create folder if not exists"""
        subtitles_folder = None
        subtitles_folder = arc_path / "subtitles"
        if not subtitles_folder.exists():
            subtitles_folder.mkdir(exist_ok=True, parents=True)
        return subtitles_folder

    def _download_from_gdrive(self, subtitles_folder):
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
            )
            print()
            print("=" * 70)
            print("✓ Download complete!")
            print(f"✓ Subtitles saved to: {subtitles_folder}")
            print("=" * 70)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading from Google Drive: {e}")
            raise

    def download(self) -> int:
        arc_path = self._setup_path()

        subtitles_folder = self._setup_subtitle_folder(arc_path)

        print(f"Downloading subtitles to: {subtitles_folder}")
        print(f"From: {self.gdrive_url}")

        self._download_from_gdrive(subtitles_folder)
        return len(list(subtitles_folder.glob("*.ass")))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    SubtitleDownloader(sys.argv[0], sys.argv[1]).download()
