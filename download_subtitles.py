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

try:
    import requests
except ImportError:
    requests = None



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

    def _extract_file_ids_from_folder(self, folder_url: str):
        """Extract file IDs from Google Drive folder page using regex."""
        if not requests:
            return None

        try:
            print("📂 Listing files from Google Drive folder...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(folder_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Extract file IDs and names using regex patterns from Google Drive's page
            files = []

            # Pattern: "id":"FILE_ID","name":"filename.ass"
            for match in re.finditer(
                r'"id":"([a-zA-Z0-9_-]{28,})","[^"]*"name":"([^"]+\.ass)"',
                response.text,
            ):
                file_id = match.group(1)
                filename = match.group(2)
                files.append((file_id, filename))

            # Remove duplicates while preserving order
            seen = set()
            unique_files = []
            for f_id, f_name in files:
                if f_id not in seen:
                    seen.add(f_id)
                    unique_files.append((f_id, f_name))

            if unique_files:
                print(f"✓ Found {len(unique_files)} file(s) in folder")
                return unique_files

            return None
        except Exception as e:
            print(f"⚠ Could not extract file IDs: {e}")
            return None

    def _download_files_individually(self, subtitles_folder, files):
        """Download files individually by file ID."""
        success_count = 0
        failed = []

        print(f"\n📥 Downloading {len(files)} file(s)...\n")

        for i, (file_id, filename) in enumerate(files, 1):
            output_file = subtitles_folder / filename

            # Skip if exists
            if output_file.exists():
                print(f"{i:2d}. ✓ {filename} (already exists)")
                success_count += 1
                continue

            print(f"{i:2d}. Downloading {filename}...", end=" ", flush=True)

            url = f"https://drive.google.com/uc?id={file_id}"
            result = subprocess.run(
                ["gdown", url, "-O", str(output_file), "-q"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and output_file.exists():
                size_mb = output_file.stat().st_size / 1024 / 1024
                print(f"✓ ({size_mb:.1f}MB)")
                success_count += 1
            else:
                print(f"✗")
                failed.append(filename)

        if failed:
            print(f"\n⚠ Failed to download: {len(failed)} file(s)")
            for name in failed:
                print(f"   - {name}")

        return success_count

    def _download_from_gdrive(self, subtitles_folder, force: bool = True):
        # Convert URL to gdown-compatible format
        gdrive_url = convert_gdrive_url(self.gdrive_url)

        # Detect if URL is a folder or individual file
        is_folder = "/folders/" in gdrive_url or "/drive/folders/" in gdrive_url

        # Count existing files before download
        existing_files = set(f.name for f in subtitles_folder.glob("*.ass"))

        if existing_files and is_folder and not force:
            # Folder already has files - assume download complete, skip download
            print(f"ℹ Found {len(existing_files)} existing subtitle(s)")
            for name in sorted(existing_files):
                print(f"   ✓ {name}")
            print("✓ Skipping download (already present)")
            return

        if is_folder:
            # For folders, use individual file download method (more reliable than gdown --folder)
            if force and existing_files:
                print(f"🔄 Force re-downloading (will replace existing {len(existing_files)} file(s))...")

            # Try to extract file IDs and download individually
            files = self._extract_file_ids_from_folder(gdrive_url)

            if files:
                # Successfully extracted file IDs - download individually
                self._download_files_individually(subtitles_folder, files)
            else:
                # Fallback to gdown --folder if extraction fails
                print("📥 Downloading subtitles (fallback method)...")
                result = subprocess.run(
                    [
                        "gdown",
                        "--folder",
                        "-O",
                        str(subtitles_folder),
                        gdrive_url,
                        "--remaining-ok",
                    ],
                    check=False,
                )
                if result.returncode != 0:
                    print("⚠ Warning: Some files could not be downloaded (may be inaccessible)")
        else:
            # Download individual file - fail if unavailable
            subprocess.run(
                [
                    "gdown",
                    "-O",
                    str(subtitles_folder),
                    gdrive_url,
                ],
                check=True,
            )

        # Count files after download
        all_files = set(f.name for f in subtitles_folder.glob("*.ass"))
        new_files = all_files - existing_files

        if new_files:
            print(f"✓ Downloaded {len(new_files)} new subtitle(s)")
            for name in sorted(new_files):
                print(f"   ✓ {name}")
        elif force and existing_files:
            print(f"✓ Re-downloaded {len(all_files)} subtitle(s)")

        print("✓ Download complete!")
        print(f"✓ Total subtitles: {len(all_files)} in {subtitles_folder}")

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

    def download(self, force: bool = True) -> int:
        arc_path = self._setup_path()

        subtitles_folder = self._setup_subtitle_folder(arc_path)

        print(f"Downloading subtitles to: {subtitles_folder}")
        print(f"From: {self.gdrive_url}")

        self._download_from_gdrive(subtitles_folder, force=force)

        # Extract any ZIP files
        self._extract_zips(subtitles_folder)

        return len(list(subtitles_folder.glob("*.ass")))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    SubtitleDownloader(sys.argv[1], sys.argv[2]).download()
