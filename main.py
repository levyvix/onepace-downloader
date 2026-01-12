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

import subprocess
import sys
import time
from pathlib import Path


def print_step(step_num: int, description: str):
    """Print formatted step header."""
    print(f"\n{'=' * 70}")
    print(f"STEP {step_num}: {description}")
    print("=" * 70)


def wait_for_downloads(folder_name: str):
    """Wait for downloads to complete by checking if .mkv files are stable."""
    print(f"\n{'=' * 70}")
    print("⏳ Waiting for episode downloads to complete...")
    print("=" * 70)
    print("\nMonitoring file sizes until stable...")
    print("(Press Ctrl+C to skip waiting and continue anyway)\n")

    folder_path = Path(folder_name)
    previous_sizes = {}
    stable_count = 0
    required_stable_checks = 3  # Files must be stable for 3 checks (15 seconds)

    try:
        while True:
            # Get current .mkv files and their sizes
            mkv_files = list(folder_path.glob("*.mkv"))

            # Check for .part files (incomplete downloads)
            part_files = list(folder_path.glob("*.part"))

            if len(part_files) > 0:
                print(
                    f"\r⏳ Downloading: {len(part_files)} file(s) still in progress...",
                    end="",
                    flush=True,
                )
                stable_count = 0
                time.sleep(5)
                continue

            # No part files, but check if we have any mkv files yet
            if len(mkv_files) == 0:
                print("\r⏳ Waiting for downloads to start...", end="", flush=True)
                stable_count = 0
                time.sleep(5)
                continue

            # Get current sizes
            current_sizes = {}
            for mkv_file in mkv_files:
                current_sizes[mkv_file.name] = mkv_file.stat().st_size

            # Compare with previous sizes
            if previous_sizes == current_sizes and len(current_sizes) > 0:
                stable_count += 1
                print(
                    f"\r⏳ Files stable ({stable_count}/{required_stable_checks})... {len(mkv_files)} file(s) downloaded",
                    end="",
                    flush=True,
                )

                if stable_count >= required_stable_checks:
                    print(
                        f"\n✓ All downloads complete! Found {len(mkv_files)} episode(s)"
                    )
                    break
            else:
                stable_count = 0
                print(
                    f"\r⏳ Downloading: {len(mkv_files)} file(s) found, sizes still changing...",
                    end="",
                    flush=True,
                )

            previous_sizes = current_sizes.copy()
            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print("\n\n⚠️  Skipping download wait (you pressed Ctrl+C)")
        print("Make sure downloads are complete before watching!")
        return

    # Give a moment for file system to sync
    time.sleep(2)
    print()


def run_script(script_name: str, args: list[str]) -> tuple[bool, str]:
    """Run a Python script with uv and return success status and output."""
    cmd = ["uv", "run"]

    cmd.extend([script_name] + args)

    print(f"\n→ Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        # Print output to user
        if result.stdout:
            print(result.stdout)
        return (result.returncode == 0, result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running {script_name}: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        return (False, e.stdout if e.stdout else "")
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user", file=sys.stderr)
        return (False, "")


def check_videos_exist(folder_name: str) -> bool:
    """Check if video files already exist in the folder."""
    folder_path = Path(folder_name)
    if not folder_path.exists():
        return False
    mkv_files = list(folder_path.glob("*.mkv"))
    return len(mkv_files) > 0


def check_subtitles_exist(folder_name: str) -> bool:
    """Check if subtitle files exist (either matched or unmatched)."""
    folder_path = Path(folder_name)
    if not folder_path.exists():
        return False

    # Check for .ass files in main folder or subtitles subfolder
    ass_files = list(folder_path.glob("*.ass"))
    subtitles_folder = folder_path / "subtitles"
    if subtitles_folder.exists():
        ass_files.extend(list(subtitles_folder.glob("*.ass")))

    return len(ass_files) > 0


def check_subtitles_matched(folder_name: str) -> bool:
    """Check if subtitles are already matched with videos."""
    folder_path = Path(folder_name)
    if not folder_path.exists():
        return False

    mkv_files = list(folder_path.glob("*.mkv"))
    if len(mkv_files) == 0:
        return False

    # Check if each video has a matching subtitle
    for mkv_file in mkv_files:
        ass_file = mkv_file.with_suffix(".ass")
        if not ass_file.exists():
            return False

    return True


def main():
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

    print("\n🎬 One Pace Download Pipeline")
    print(f"\nNyaa URL: {nyaa_url}")
    print(f"GDrive URL: {gdrive_url}")
    print(f"Folder: {folder_name}")

    # Step 1: Download episodes
    print_step(1, "Downloading episodes from nyaa.si")

    videos_existed = check_videos_exist(folder_name)
    step1_executed = False

    if videos_existed:
        print(f"⏭️  Skipping: Video files already exist in {folder_name}/")
        print(f"   Found {len(list(Path(folder_name).glob('*.mkv')))} .mkv files")
    else:
        success, output = run_script("magnet_downloader.py", [nyaa_url, folder_name])
        if not success:
            print("\n✗ Pipeline failed at step 1 (download episodes)")
            sys.exit(1)

        step1_executed = True

    # Step 2: Download subtitles
    print_step(2, "Downloading subtitles from Google Drive")
    if check_subtitles_exist(folder_name):
        folder_path = Path(folder_name)
        ass_count = len(list(folder_path.glob("*.ass")))
        subtitles_folder = folder_path / "subtitles"
        if subtitles_folder.exists():
            ass_count += len(list(subtitles_folder.glob("*.ass")))
        print("⏭️  Skipping: Subtitle files already exist")
        print(f"   Found {ass_count} .ass files")
    else:
        success, _ = run_script("download_subtitles.py", [gdrive_url, folder_name])
        if not success:
            print("\n✗ Pipeline failed at step 2 (download subtitles)")
            sys.exit(1)

    # Wait for episode downloads to complete
    if step1_executed:
        # We just added torrents, need to wait for them
        wait_for_downloads(folder_name)
    elif not check_videos_exist(folder_name):
        # Videos don't exist yet, might still be downloading
        print(f"\n{'=' * 70}")
        print("✓ Checking if downloads are still in progress...")
        print("=" * 70)

        folder_path = Path(folder_name)
        if folder_path.exists():
            # Check for incomplete downloads (.part files) or ongoing downloads
            part_files = list(folder_path.glob("*.part"))
            mkv_files = list(folder_path.glob("*.mkv"))

            if len(part_files) > 0 or len(mkv_files) > 0:
                print("⏳ Found files downloading or incomplete, waiting...")
                wait_for_downloads(folder_name)
            else:
                print("✓ No active downloads found\n")
        else:
            print("✓ Folder doesn't exist yet\n")

    # Step 3: Match subtitles to videos
    print_step(3, "Matching subtitles to video filenames")
    if check_subtitles_matched(folder_name):
        mkv_count = len(list(Path(folder_name).glob("*.mkv")))
        print("⏭️  Skipping: Subtitles already matched with videos")
        print(f"   All {mkv_count} videos have matching .ass files")
    else:
        success, _ = run_script(
            "match_onepace_subtitles.py", [folder_name, folder_name]
        )
        if not success:
            print("\n✗ Pipeline failed at step 3 (match subtitles)")
            sys.exit(1)

    # Step 4: Verify all matched
    print_step(4, "Verifying all videos have matching subtitles")
    success, _ = run_script("verify_subtitles.py", [folder_name])
    if not success:
        print("\n✗ Pipeline failed at step 4 (verify)")
        sys.exit(1)

    print(f"\n{'=' * 70}")
    print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nAll episodes and subtitles ready in: {folder_name}/")
    print(
        "\n🎉 Ready to watch! Your video player will automatically load the subtitles."
    )
    print("\n💡 Note: transmission-cli may still be running in background (seeding).")
    print("   This is normal. Stop seeding with: killall transmission-cli")


if __name__ == "__main__":
    main()
