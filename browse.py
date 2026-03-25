"""
One Pace Interactive Browser with Scraping & fzf Selection

Scrapes https://onepaceptbr.github.io/ to list sagas and arcos, then offers
interactive selection via fzf to automatically execute the complete download pipeline.

Usage:
    uv run browse.py

Requires system packages:
    - fzf (install: sudo pacman -S fzf / apt install fzf / brew install fzf)
    - curl (usually pre-installed)
    - transmission-cli (for episode downloads)
"""

import re
import sys
import time
import subprocess
from pyfzf.pyfzf import FzfPrompt

from pathlib import Path
from main import (
    MagnetDownloader,
    SubtitleDownloader,
    flatten_video_folders,
    get_summary,
    print_step,
    print_separator,
)
from match_onepace_subtitles import extract_episode_number, guess_arc_name

SITE_BASE = "https://onepaceptbr.github.io"


def fetch_html(url: str) -> str:
    """Fetch HTML from URL using curl."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--compressed", url],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"curl failed with code {result.returncode}")
        if not result.stdout:
            raise RuntimeError(f"Empty response from {url}")
        return result.stdout
    except FileNotFoundError:
        print("✗ curl não encontrado. Instale com: sudo pacman -S curl")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout ao baixar {url}")
        sys.exit(1)


def parse_sagas(html: str) -> list[dict]:
    """Extract sagas from main page."""
    pattern = r'href="(https://onepaceptbr\.github\.io/[^"]+)"[^>]*>.*?<h[23][^>]*>([^<]+)</h[23]>'
    matches = re.findall(pattern, html, re.DOTALL)

    sagas = []
    for url, name in matches:
        name = name.strip()
        if "saga" in name.lower() or "especiais" in name.lower():
            sagas.append({"name": name, "url": url})

    return sagas


def parse_arcs(html: str) -> list[dict]:
    """Extract arcs from saga page. Handles two formats: popup and direct link."""
    arcs = []

    # Format 1: Popup with both nyaa and gdrive links
    popup_pattern = r'onclick="abrirPopup\(this,\s*\'([^\']+)\',\s*\'([^\']+)\'\)".*?<h3>([^<]+)</h3>'
    popup_matches = re.findall(popup_pattern, html, re.DOTALL)
    for nyaa_url, gdrive_url, name in popup_matches:
        arcs.append(
            {
                "name": name.strip(),
                "nyaa_url": nyaa_url.strip(),
                "gdrive_url": gdrive_url.strip(),
            }
        )

    # Format 2: Direct link (nyaa only, no popup)
    direct_pattern = r'<a\s+href="(https://nyaa\.si/[^"]+)"\s+class="arc"[^>]*>.*?<h3>([^<]+)</h3>'
    direct_matches = re.findall(direct_pattern, html, re.DOTALL)
    for nyaa_url, name in direct_matches:
        arcs.append(
            {
                "name": name.strip(),
                "nyaa_url": nyaa_url.strip(),
                "gdrive_url": None,
            }
        )

    # Filter out arcs without any link
    arcs = [arc for arc in arcs if arc["nyaa_url"] or arc["gdrive_url"]]

    return arcs


def generate_folder_name(arc_name: str) -> str:
    """Convert arc name to folder name: 'Arco 8 - Reverse Mountain' → 'arc08-reverse-mountain'."""
    match = re.match(r"Arco\s+([\d.]+)\s*-\s*(.+)", arc_name.strip())
    if not match:
        # Fallback for names without standard pattern
        slug = arc_name.lower().replace(" ", "-")
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug

    num_str, name = match.group(1), match.group(2).strip()

    # Zero-pad only integers < 10
    if "." not in num_str and int(num_str) < 10:
        num_padded = num_str.zfill(2)
    else:
        num_padded = num_str

    # Normalize name: lowercase, spaces→hyphens, remove special chars
    name = name.lower().replace(" ", "-").replace("'", "")
    name = re.sub(r"[^a-z0-9-]", "", name)
    name = re.sub(r"-+", "-", name).strip("-")

    return f"arc{num_padded}-{name}"


def get_arc_status(arc: dict) -> str:
    """Return display status for an arc."""
    has_nyaa = bool(arc["nyaa_url"])
    has_gdrive = bool(arc["gdrive_url"])

    if has_nyaa and has_gdrive:
        return "[nyaa+gdrive]"
    elif has_nyaa:
        return "[apenas nyaa]"
    else:
        return "[apenas gdrive]"


def run_fzf(items: list[str], prompt: str = "Select: ") -> str | None:
    """Run fzf with given items and return selected item, or None if cancelled."""
    try:
        fzf = FzfPrompt()
        result = fzf.prompt(items, fzf_options=f"--prompt '{prompt}' --height 40% --reverse")
        if result:
            return result[0]
        return None
    except FileNotFoundError:
        print("✗ fzf não encontrado. Instale com: sudo pacman -S fzf")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠ Cancelado pelo usuário")
        sys.exit(0)


def wait_for_videos(folder_name: str, timeout: int = 30) -> bool:
    """Wait for video files to appear in folder (with metadata).

    Sometimes videos take a moment to fully appear in the filesystem.
    Returns True if videos found, False if timeout.
    """
    folder_path = Path(folder_name)
    start_time = time.time()

    while time.time() - start_time < timeout:
        videos = list(folder_path.rglob("*.mkv"))
        if videos:
            # Found videos, wait a bit more for metadata to settle
            time.sleep(1)
            return True
        time.sleep(0.5)

    return False


def match_subtitles(folder_name: str) -> int:
    """Match and rename subtitles to video filenames.

    Returns number of successfully matched subtitles.
    """
    folder_path = Path(folder_name)
    subtitle_dir = folder_path / "subtitles"

    if not subtitle_dir.exists():
        return 0

    # Wait for videos to appear
    if not wait_for_videos(folder_name, timeout=30):
        return 0

    # Get all video files (recursively, in case they're in subfolders)
    videos = sorted([f for f in folder_path.rglob("*.mkv")])
    subtitles = sorted([f for f in subtitle_dir.glob("*.ass")])

    if not videos or not subtitles:
        return 0

    # Guess arc name from videos
    arc_name = guess_arc_name(videos)

    # Build subtitle map by episode number
    subtitle_map: dict[str, Path] = {}
    for sub in subtitles:
        ep_num = extract_episode_number(sub.name, arc_name or "")
        if ep_num:
            subtitle_map[ep_num] = sub

    # Match and rename
    matched_count = 0
    for video in videos:
        ep_num = extract_episode_number(video.name, arc_name or "")
        if ep_num and ep_num in subtitle_map:
            old_sub = subtitle_map[ep_num]
            new_sub_name = video.name.replace(".mkv", ".ass")
            # Put subtitle in the same directory as the video
            new_sub_path = video.parent / new_sub_name

            try:
                old_sub.rename(new_sub_path)
                matched_count += 1
            except Exception:
                pass  # Silent fail, continue

    return matched_count


def run_pipeline(arc: dict, folder_name: str) -> None:
    """Execute the download pipeline with selected arc data."""
    nyaa_url = arc["nyaa_url"]
    gdrive_url = arc["gdrive_url"]

    print_separator()
    print(f"🚀 Starting pipeline for: {arc['name']}")
    print(f"   Folder: {folder_name}")
    print_separator()

    # Step 1: Download episodes (if nyaa available)
    if nyaa_url:
        print_step(1, "Downloading episodes from nyaa.si")
        count_episodes = MagnetDownloader(nyaa_url, folder_name).download()
        if count_episodes > 0:
            print(f"✓ {count_episodes} episodes downloaded!")
        else:
            print("ℹ No episodes found in search results")
    else:
        print_step(1, "Skipping nyaa (not available for this arc)")

    # Step 2: Download subtitles (if gdrive available)
    if gdrive_url:
        print_step(2, "Downloading subtitles from Google Drive")
        count_subtitles = SubtitleDownloader(gdrive_url, folder_name).download()
        if count_subtitles > 0:
            print(f"✓ {count_subtitles} subtitles downloaded!")
        else:
            print("ℹ No subtitles found in drive")
    else:
        print_step(2, "Skipping gdrive (not available for this arc)")

    # Step 2.5: Flatten video folders
    print_separator()
    print("🔍 Checking for videos in subdirectories...")
    print_separator()
    moved_count = flatten_video_folders(folder_name)
    if moved_count > 0:
        print(f"\n✓ Moved {moved_count} video(s) to main folder")
    else:
        print("\n✓ All videos are already in the main folder")

    # Step 2.75: Match subtitles to videos
    if gdrive_url:
        print_separator()
        print("🎬 Matching subtitles to videos...")
        print_separator()
        matched_count = match_subtitles(folder_name)
        if matched_count > 0:
            print(f"✓ Matched {matched_count} subtitle(s) to video(s)")
        else:
            print("ℹ Could not match subtitles automatically")

    # Step 3: Show summary
    print_step(3, "Download Summary")
    ass_files, mkv_files = get_summary(folder_name)
    print(f"✓ Videos downloaded: {len(mkv_files)}")
    print(f"✓ Subtitles downloaded: {len(ass_files)}")

    print_separator()
    print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
    print_separator()

    if mkv_files and ass_files:
        print("\n✓ Videos and subtitles are ready!")
        print("   You can now watch with: mpv " + folder_name + "/")


def main() -> None:
    """Main interactive flow: fetch sagas → select saga → fetch arcs → select arc → run pipeline."""
    print("\n📚 One Pace Interactive Browser\n")

    # Step 1: Fetch and display sagas
    print("🔄 Loading sagas...")
    html = fetch_html(SITE_BASE)
    sagas = parse_sagas(html)

    if not sagas:
        print("✗ No sagas found on the website")
        sys.exit(1)

    saga_names = [saga["name"] for saga in sagas]
    selected_saga_name = run_fzf(saga_names, "Select saga: ")
    if not selected_saga_name:
        print("✗ No saga selected")
        sys.exit(1)

    selected_saga = next(s for s in sagas if s["name"] == selected_saga_name)
    print(f"\n✓ Selected: {selected_saga_name}\n")

    # Step 2: Fetch and display arcs
    print("🔄 Loading arcs...")
    html = fetch_html(selected_saga["url"])
    arcs = parse_arcs(html)

    if not arcs:
        print("✗ No arcs found in this saga")
        sys.exit(1)

    # Build display strings with status
    arc_displays = [
        f"{arc['name']:<40} {get_arc_status(arc)}" for arc in arcs
    ]

    selected_display = run_fzf(arc_displays, "Select arc: ")
    if not selected_display:
        print("✗ No arc selected")
        sys.exit(1)

    # Extract original arc name from display string
    arc_name = selected_display.split("[")[0].strip()
    selected_arc = next(arc for arc in arcs if arc["name"] == arc_name)
    folder_name = generate_folder_name(arc_name)

    print(f"\n✓ Selected: {arc_name}")
    print(f"   Folder: {folder_name}\n")

    # Step 3: Confirm before running
    print_separator()
    print("Confirming download details:")
    print(f"  Arc: {selected_arc['name']}")
    print(f"  Folder: {folder_name}")
    if selected_arc["nyaa_url"]:
        print(f"  Nyaa: {selected_arc['nyaa_url'][:60]}...")
    if selected_arc["gdrive_url"]:
        print(f"  Drive: {selected_arc['gdrive_url'][:60]}...")
    print_separator()

    confirm = input("Continue with download? (Y/n): ").strip().lower()
    if confirm == "n":
        print("✗ Cancelled")
        sys.exit(0)

    # Step 4: Run pipeline
    print()
    run_pipeline(selected_arc, folder_name)


if __name__ == "__main__":
    main()
