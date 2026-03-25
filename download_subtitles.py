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

import re
import subprocess
import sys
import zipfile
from pathlib import Path


def convert_gdrive_url(url: str) -> str:
    """Convert Google Drive URL formats to gdown-compatible format.

    Converts:
    - /file/d/ID/view?... → /uc?id=ID
    - /drive/folders/ID → /drive/folders/ID (unchanged, folder format)
    """
    # Extract file ID from /file/d/ID/view format
    file_match = re.search(r'/file/d/([a-zA-Z0-9-_]+)', url)
    if file_match:
        file_id = file_match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"

    # Already in correct format or folder format - return as-is
    return url


class SubtitleDownloader:
    """Download One Pace subtitles from Google Drive."""

    def __init__(self, gdrive_url: str, arc_folder: str) -> None:
        self.gdrive_url = gdrive_url
        self.arc_folder = arc_folder
        self.zip_password = None

    def set_password(self, password: str) -> None:
        """Set password for encrypted ZIP files."""
        self.zip_password = password

    def _setup_path(self):
        """Setup arc path object and create folder if not exists"""
        arc_path = Path(self.arc_folder)
        arc_path.mkdir(parents=True, exist_ok=True)
        return arc_path

    def _setup_subtitle_folder(self, arc_path: Path):
        """Setup subtiles/ folder inside arc path, and create folder if not exists"""
        subtitles_folder = arc_path / "subtitles"
        subtitles_folder.mkdir(exist_ok=True, parents=True)
        return subtitles_folder

    def _download_from_gdrive(self, subtitles_folder):
        # Convert URL to gdown-compatible format
        gdrive_url = convert_gdrive_url(self.gdrive_url)

        # Detect if URL is a folder or individual file
        is_folder = "/folders/" in gdrive_url or "/drive/folders/" in gdrive_url

        if is_folder:
            # Download entire folder
            subprocess.run(
                [
                    "gdown",
                    "--folder",
                    "-O",
                    str(subtitles_folder),
                    gdrive_url,
                    "--remaining-ok",
                ],
                check=True,
            )
        else:
            # Download individual file
            subprocess.run(
                [
                    "gdown",
                    "-O",
                    str(subtitles_folder),
                    gdrive_url,
                ],
                check=True,
            )

        print("✓ Download complete!")
        print(f"✓ Subtitles saved to: {subtitles_folder}")

    def _extract_zips(self, folder: Path) -> int:
        """Extract any ZIP files found in folder and return count of extracted files."""
        zip_files = list(folder.glob("*.zip"))
        if not zip_files:
            return 0

        print(f"\n📦 Found {len(zip_files)} ZIP file(s), extracting...")
        extracted_count = 0

        for zip_file in zip_files:
            try:
                # Convert password to bytes if provided
                pwd = None
                if self.zip_password:
                    pwd = self.zip_password.encode("utf-8")

                with zipfile.ZipFile(zip_file, "r") as z:
                    z.extractall(folder, pwd=pwd)
                    print(f"   ✓ Extracted: {zip_file.name}")
                    # Count extracted files
                    extracted_count += len(z.namelist())

                # Remove the zip after extraction
                zip_file.unlink()
                print(f"   ✓ Removed: {zip_file.name}")
            except zipfile.BadZipFile:
                print(f"   ✗ Bad ZIP file: {zip_file.name}")
            except RuntimeError as e:
                if "Bad password" in str(e):
                    print(f"   ✗ Wrong password for {zip_file.name}")
                else:
                    print(f"   ✗ Error extracting {zip_file.name}: {e}")
            except Exception as e:
                print(f"   ✗ Error extracting {zip_file.name}: {e}")

        return extracted_count

    def download(self) -> int:
        arc_path = self._setup_path()

        subtitles_folder = self._setup_subtitle_folder(arc_path)

        print(f"Downloading subtitles to: {subtitles_folder}")
        print(f"From: {self.gdrive_url}")

        self._download_from_gdrive(subtitles_folder)

        # Extract any ZIP files
        self._extract_zips(subtitles_folder)

        return len(list(subtitles_folder.glob("*.ass")))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    SubtitleDownloader(sys.argv[1], sys.argv[2]).download()
