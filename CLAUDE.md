# One Pace Download & Subtitle Workflow

## Overview

Simple, clean workflow for downloading One Pace episodes and matching them with subtitles.

**What it does:**
1. Downloads episodes from nyaa.si via torrent
2. Downloads subtitles from Google Drive
3. Automatically renames subtitles to match video filenames
4. Verifies everything matched correctly

Video players automatically load subtitles when filenames match (except extension).

---

## Quick Start - One Command Pipeline

**Easiest way:** Run the entire workflow with a single command!

```bash
uv run onepace_pipeline.py "<NYAA_URL>" "<GDRIVE_URL>" "<FOLDER_NAME>"
```

**Examples:**
```bash
# With "arc" prefix (used exactly as-is)
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Without "arc" prefix (auto-adds "arc-")
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+skypiea" \
  "https://drive.google.com/drive/folders/1ABC..." \
  "skypiea"
# Creates: arc-skypiea/
```

**What you need to provide:**
1. **Nyaa.si URL** - Search results or single torrent page
2. **Google Drive URL** - Subtitle folder link
3. **Folder name** - Exact folder name you want to use (e.g., "arc15-jaya", "skypiea", "water7")
   - If name starts with "arc", uses it exactly as-is
   - Otherwise, auto-prefixes with "arc-" (e.g., "jaya" → "arc-jaya")

**What it does automatically:**
1. ✓ Starts downloading all episodes from nyaa.si
2. ✓ Downloads all subtitles from Google Drive
3. ✓ Waits for episode downloads to complete (monitors transmission progress)
4. ✓ Matches subtitles to video filenames
5. ✓ Verifies everything matched correctly

**Notes:**
- The pipeline will wait for torrent downloads to finish before matching subtitles
- You can press Ctrl+C during the wait to skip and continue manually later
- **Safe to re-run!** If the pipeline fails or is interrupted, just run the same command again - it will skip completed steps

---

## Manual 4-Step Workflow (Advanced)

If you prefer to run each step manually or need more control:

```bash
cd ~/Downloads/onepace

# Step 1: Download episodes
uv run magnet_downloader.py "<NYAA_URL>" "<FOLDER_NAME>"

# Step 2: Download subtitles (while videos download)
uv run --with gdown download_subtitles.py "<GDRIVE_URL>" "<FOLDER_NAME>"

# Step 3: Match subtitles to videos
uv run match_onepace_subtitles.py "<FOLDER_NAME>" "<FOLDER_NAME>"

# Step 4: Verify everything matched
uv run verify_subtitles.py "<FOLDER_NAME>"
```

**Note:** Folder naming is consistent across all scripts - whatever name you use will be used everywhere.

---

## Script Reference

### 0. `onepace_pipeline.py` - Complete Workflow Pipeline ⭐

Runs all 4 steps automatically in a single command.

**Usage:**
```bash
uv run onepace_pipeline.py <nyaa_url> <gdrive_url> <folder_name>
```

**Example:**
```bash
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"
```

**What it does:**
1. Starts episode downloads via `magnet_downloader.py` (non-blocking)
2. Downloads subtitles via `download_subtitles.py` (runs while episodes download)
3. **Waits for episode downloads to complete** (monitors transmission progress)
4. Matches subtitles via `match_onepace_subtitles.py`
5. Verifies results via `verify_subtitles.py`

**Features:**
- ✓ **Idempotent** - Safe to re-run after failures, skips completed steps
- ✓ Downloads episodes and subtitles in parallel (saves time!)
- ✓ **Smart download detection** - Waits until file sizes are stable (not changing)
- ✓ Works with seeding - Doesn't wait for transmission-cli to exit
- ✓ Shows download progress in real-time
- ✓ Press Ctrl+C during wait to skip and continue later
- ✓ Formatted progress output for each step
- ✓ Stops if any step fails
- ✓ Shows clear success/error messages

**Idempotency checks:**
- Step 1: Skips if .mkv files already exist in folder
- Step 2: Skips if .ass files already exist (in folder or subtitles/)
- Step 3: Skips if all videos already have matching .ass files
- Step 4: Always runs (verification is cheap and safe)

**Download detection:**
- Checks for .part files (incomplete downloads)
- Monitors .mkv file sizes every 5 seconds
- Downloads considered complete when sizes stable for 15 seconds
- transmission-cli can continue seeding in background

---

### 1. `magnet_downloader.py` - Download Episodes

Extracts magnet links from nyaa.si and downloads them asynchronously.

**Usage:**
```bash
uv run magnet_downloader.py <nyaa_url> <arc_name>
```

**Examples:**
```bash
# From search results
uv run magnet_downloader.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  jaya

# From single torrent page
uv run magnet_downloader.py \
  "https://nyaa.si/view/1234567" \
  thriller_bark
```

**Output:**
- Creates: `arc<n>-title/` folder
- Downloads start immediately in background
- Check progress: `ps aux | grep transmission-cli` or transmission-qt GUI

---

### 2. `download_subtitles.py` - Download Subtitles

Downloads subtitle files from Google Drive folder.

**Usage:**
```bash
uv run download_subtitles.py <gdrive_url> <arc_name>
```

**Examples:**
```bash
# Auto-detect arc number
uv run download_subtitles.py \
  "https://drive.google.com/drive/folders/1ABC..." \
  "<arcN>-title"

# With explicit folder name
uv run download_subtitles.py \
  "https://drive.google.com/drive/folders/1ABC..." \
  "arc<n>-title"
```

**Output:**
- Saves subtitles to: `arc<n>-title/`
- Example: `arc15-jaya/Jaya 01.ass`, `arc15-jaya/Jaya 02.ass`

---

### 3. `match_onepace_subtitles.py` - Match Subtitles to Videos

Renames subtitle files to match video filenames exactly.

**Usage:**
```bash
uv run match_onepace_subtitles.py <video_dir> <subtitle_dir>
```

**Example:**
```bash
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya/subtitles"
```

**What it does:**
- Finds all `.mkv` videos and `.ass` subtitles
- Extracts episode numbers from filenames
- Matches by episode number
- Renames: `Jaya 01.ass` → `[One Pace][218-220] Jaya 01 [1080p][HASH].ass`

**Supported patterns:**
- "Arc Name 01.ass"
- "46 - Arc Name 04.ass"
- Various other common patterns

---

### 4. `verify_subtitles.py` - Verify All Matched

Checks that every video file has a matching subtitle file.

**Usage:**
```bash
uv run verify_subtitles.py <directory>
```

**Example:**
```bash
uv run verify_subtitles.py "arc15-jaya"
```

**Output:**
```
Checking 25 video files in: arc15-jaya
======================================================================
✓ [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
  → [One Pace][218-220] Jaya 01 [1080p][HASH].ass

✓ [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
  → [One Pace][221-224] Jaya 02 [1080p][HASH].ass

... (more files) ...

======================================================================
Result: 25/25 videos have matching subtitles
✓ All videos have matching subtitle files!
```

---

## Example: Download Jaya Arc

**Option 1: One-Command Pipeline (Recommended)**

```bash
cd ~/Downloads/onepace

# Single command - entire workflow
uv run onepace_pipeline.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Output:
# ======================================================================
# STEP 1: Downloading episodes from nyaa.si
# ✓ Created: arc15-jaya/
# ✓ Starting downloads...
#
# STEP 2: Downloading subtitles from Google Drive
# ✓ Downloaded 25 subtitle files
#
# ======================================================================
# ⏳ Waiting for episode downloads to complete...
# ======================================================================
# Monitoring file sizes until stable...
# (Press Ctrl+C to skip waiting and continue anyway)
#
# ⏳ Downloading: 25 file(s) found, sizes still changing...
# ⏳ Files stable (1/3)... 25 file(s) downloaded
# ⏳ Files stable (2/3)... 25 file(s) downloaded
# ⏳ Files stable (3/3)... 25 file(s) downloaded
# ✓ All downloads complete! Found 25 episode(s)
#
# STEP 3: Matching subtitles to video filenames
# ✓ Matched and renamed 25 subtitle files
#
# STEP 4: Verifying all videos have matching subtitles
# Result: 25/25 videos have matching subtitles
# ======================================================================
# ✓ PIPELINE COMPLETED SUCCESSFULLY!
# 🎉 Ready to watch! Your video player will automatically load the subtitles.
```

**Option 2: Manual Step-by-Step**

```bash
cd ~/Downloads/onepace

# Step 1: Download episodes
uv run magnet_downloader.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  "arc15-jaya"

# Step 2: Download subtitles
uv run --with gdown download_subtitles.py \
  "https://drive.google.com/drive/folders/1XYZ..." \
  "arc15-jaya"

# Step 3: Match subtitles
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya"

# Step 4: Verify
uv run verify_subtitles.py "arc15-jaya"
```

---

## Folder Structure After Workflow

**Before:**
```
arc15-jaya/
├── [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
├── [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
└── Jaya 01.ass
└── Jaya 02.ass
```

**After (matched):**
```
arc15-jaya/
├── [One Pace][218-220] Jaya 01 [1080p][HASH].mkv
├── [One Pace][218-220] Jaya 01 [1080p][HASH].ass  ← Matched!
├── [One Pace][221-224] Jaya 02 [1080p][HASH].mkv
└── [One Pace][221-224] Jaya 02 [1080p][HASH].ass  ← Matched!
```

---

## Re-running After Failures

The pipeline is **idempotent** - safe to re-run multiple times!

**Example: Network failure during subtitle download**

```bash
# First run - fails during step 2
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ✓ Episodes downloading
# STEP 2: ✗ Network error!

# Second run - resumes where it left off
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ⏭️ Skipping - 25 .mkv files already exist
# STEP 2: ✓ Downloads subtitles successfully
# STEP 3: ✓ Matches subtitles
# STEP 4: ✓ Verifies
```

**Example: Ctrl+C during torrent wait**

```bash
# First run - user interrupts
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ✓ Torrents started
# STEP 2: ✓ Subtitles downloaded
# ⏳ Waiting for torrents... [Ctrl+C pressed]

# Wait for torrents to finish manually...
ps aux | grep transmission-cli

# Second run - completes matching
uv run onepace_pipeline.py "<URL1>" "<URL2>" "arc15-jaya"
# STEP 1: ⏭️ Skipping - videos exist
# STEP 2: ⏭️ Skipping - subtitles exist
# ✓ No active torrents
# STEP 3: ✓ Matches subtitles
# STEP 4: ✓ Verifies
```

---

## Troubleshooting

### Want to skip waiting for downloads?
- **During wait:** Press `Ctrl+C` to skip the wait and continue later
- **Manual match later:** Run `uv run match_onepace_subtitles.py "<folder>" "<folder>"` after downloads finish
- **Check download status:** `ls -lh <folder>/*.mkv` to see file sizes

### Pipeline says "files stable" but downloads still active?
- **This is normal!** The pipeline detects when downloads are **complete** (file sizes stable)
- transmission-cli continues running in background for **seeding** - this is expected
- You can stop seeding later: `killall transmission-cli` (after pipeline finishes)

### Downloads not starting?
- **Check:** `ps aux | grep transmission-cli` to see active downloads
- **Check files:** `ls -lh <folder>/` to see what's downloaded
- **Fix:** Make sure transmission-cli is installed
- **Alternative:** Use transmission-qt (GUI) to monitor downloads

### No subtitle files downloaded?
- **Check:** Google Drive link is accessible in browser
- **Fix:** Verify folder is shared "Anyone with link"

### "Could not extract episode number"?
- **Issue:** Subtitle filenames don't match expected patterns
- **Fix:** Rename subtitles to include episode numbers (e.g., "Arc Name 01.ass")

### Script says no matches found?
- **Check:** Video and subtitle episode numbers match
- **Check:** Both files in correct directories

### Wrong folder name like "arc-arc20" created?
- **Issue:** `magnet_downloader.py` auto-prefixes "arc-" to the arc_name parameter, so passing "arc20" creates "arc-arc20"
- **Fix:** Pass only the arc NUMBER (like "20") or arc NAME (like "sabaody"), not "arc20"
- **Examples:**
  ```bash
  # WRONG - creates "arc-arc20"
  uv run magnet_downloader.py "<URL>" "arc20"

  # CORRECT - creates "arc-20" or "arc20-sabaody"
  uv run magnet_downloader.py "<URL>" "20"
  uv run magnet_downloader.py "<URL>" "sabaody"
  ```
- **For subtitles:** Use the folder name created by magnet_downloader, not the arc_name

---

## Dependencies

**Required:**
- Python 3.6+
- transmission-cli (for downloading)
- uv (for running scripts)

**Optional packages:**
- `gdown` (auto-installed when running download_subtitles.py with `--with gdown`)

**Install transmission-cli:**
```bash
# Arch Linux
sudo pacman -S transmission-cli

# macOS
brew install transmission-cli

# Debian/Ubuntu
sudo apt install transmission-cli
```

---

## Files in This Project

- `onepace_pipeline.py` - **ONE-COMMAND PIPELINE** - Runs entire workflow automatically
- `magnet_downloader.py` - Downloads episodes from nyaa.si
- `download_subtitles.py` - Downloads subtitles from Google Drive
- `match_onepace_subtitles.py` - Renames subtitles to match videos
- `verify_subtitles.py` - Verifies all videos have matching subtitles
- `CLAUDE.md` - This documentation

