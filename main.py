"""
One Pace Download Pipeline
Executes the complete workflow: download episodes, download subtitles, match, and verify.

Usage:
    uv run main.py <nyaa_url> <gdrive_url> <folder_name>

Example:
    uv run main.py \
        "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
        "https://drive.google.com/drive/folders/1XYZ..." \
        "arc15-jaya"
"""

import sys
from pathlib import Path
from magnet_downloader import MagnetDownloader
from download_subtitles import SubtitleDownloader


def print_step(step_num: int, description: str):
    """Print formatted step header."""
    print(f"\n{'=' * 70}")
    print(f"STEP {step_num}: {description}")
    print("=" * 70)


def flatten_video_folders(folder_name: str) -> int:
    """
    Detect and move .mkv files from subdirectories to the main folder.
    Some torrents download a folder containing the videos instead of the videos directly.

    Returns:
        Number of files moved
    """
    folder_path = Path(folder_name)
    if not folder_path.exists():
        return 0

    moved_count = 0

    # Find all subdirectories (excluding 'subtitles' folder)
    subdirs = [d for d in folder_path.iterdir() if d.is_dir() and d.name != "subtitles"]

    for subdir in subdirs:
        # Find all .mkv files in this subdirectory
        mkv_files = list(subdir.glob("*.mkv"))

        if len(mkv_files) > 0:
            print(f"\n📁 Found {len(mkv_files)} video(s) in subfolder: {subdir.name}")

            for mkv_file in mkv_files:
                target = folder_path / mkv_file.name

                # Move the file
                try:
                    mkv_file.rename(target)
                    print(f"   ✓ Moved: {mkv_file.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ✗ Error moving {mkv_file.name}: {e}")

            # Try to remove the empty directory
            try:
                if not list(subdir.iterdir()):  # Only if empty
                    subdir.rmdir()
                    print(f"   ✓ Removed empty folder: {subdir.name}")
                else:
                    print(f"   ⚠ Folder not empty, keeping: {subdir.name}")
            except Exception as e:
                print(f"   ⚠ Could not remove folder: {e}")

    return moved_count


def download_episodes(folder_name, nyaa_url) -> int:
    downloader = MagnetDownloader(nyaa_url, folder_name)
    how_many = downloader.download()
    return how_many


def download_subtitles(folder_name, gdrive_url) -> int:
    sub_downloader = SubtitleDownloader(gdrive_url, folder_name)
    how_many = sub_downloader.download()
    return how_many


def get_parameters():
    if len(sys.argv) != 4:
        print("Usage: uv run onepace_pipeline.py <nyaa_url> <gdrive_url> <folder_name>")
        print("\nExample:")
        print("  uv run onepace_pipeline.py \\")
        print('    "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \\')
        print('    "https://drive.google.com/drive/folders/1XYZ..." \\')
        print('    "arc15-jaya"')
        sys.exit(1)

    nyaa_url = sys.argv[1]
    gdrive_url = sys.argv[2]
    folder_name = sys.argv[3]
    return folder_name, gdrive_url, nyaa_url


def get_summary(folder_name):
    folder_path = Path(folder_name)
    mkv_files = list(folder_path.glob("*.mkv"))
    ass_files = list(folder_path.glob("*.ass"))

    # Also check subtitles folder
    subtitles_folder = folder_path / "subtitles"
    if subtitles_folder.exists():
        ass_files.extend(list(subtitles_folder.glob("*.ass")))
    return ass_files, mkv_files


def main():
    folder_name, gdrive_url, nyaa_url = get_parameters()

    print("\n🎬 One Pace Download Pipeline")
    print(f"\nNyaa URL: {nyaa_url}")
    print(f"GDrive URL: {gdrive_url}")
    print(f"Folder: {folder_name}")

    # Step 1: Download episodes
    print_step(1, "Downloading episodes from nyaa.si")

    count_episodes = download_episodes(folder_name, nyaa_url)
    if count_episodes > 0:
        print(f"{count_episodes} episodes downloaded!")

    # Step 2: Download subtitles
    print_step(2, "Downloading subtitles from Google Drive")
    count_subtitles = download_subtitles(folder_name, gdrive_url)
    if count_subtitles > 0:
        print(f"{count_subtitles} subtitles downloaded!")

    # Step 2.5: Flatten video folders (move videos from subdirectories)
    print(f"\n{'=' * 70}")
    print("🔍 Checking for videos in subdirectories...")
    print("=" * 70)

    moved_count = flatten_video_folders(folder_name)

    if moved_count > 0:
        print(f"\n✓ Moved {moved_count} video(s) to main folder")
    else:
        print("\n✓ All videos are already in the main folder")

    # Step 3: Show summary
    print_step(3, "Download Summary")
    ass_files, mkv_files = get_summary(folder_name)

    print(f"✓ Videos downloaded: {len(mkv_files)}")
    print(f"✓ Subtitles downloaded: {len(ass_files)}")

    print(f"\n{'=' * 70}")
    print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
