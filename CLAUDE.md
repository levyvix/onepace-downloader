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

## The 4-Step Workflow

When you ask me to download an arc, provide:
1. **Arc name or number** (e.g., "Arc 15: Jaya", "20: Sabaody", or just "20" / "sabaody")
2. **Nyaa.si URL** (search results or single torrent page)
3. **Google Drive folder link** (subtitles)

**Important:** For magnet_downloader.py, use just the arc number or name (e.g., "20" or "sabaody"), NOT "arc20". The script auto-prefixes "arc-" to avoid duplicate folder names.

I'll run these 4 commands in order:

```bash
cd ~/Downloads/onepace

# Step 1: Download episodes
uv run magnet_downloader.py "<NYAA_URL>" "arc_folder"

# Step 2: Download subtitles (while videos download)
uv run --with gdown download_subtitles.py "<GDRIVE_URL>" "arc_folder"

# Step 3: Match subtitles to videos
uv run match_onepace_subtitles.py "arc_folder" "arc_folder/subtitles"

# Step 4: Verify everything matched
uv run verify_subtitles.py "arc_folder"
```

---

## Script Reference

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
- Check progress: `transmission-remote -l`

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

```bash
cd ~/Downloads/onepace

# Step 1: Download episodes
# You provide: https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya
uv run magnet_downloader.py \
  "https://nyaa.si/?f=0&c=0_0&q=one+pace+jaya" \
  jaya

# ✓ Created: arc15-jaya/
# ✓ Starting downloads...

# Step 2: Download subtitles
# You provide: https://drive.google.com/drive/folders/1XYZ...
uv run --with gdown download_subtitles.py \
  "https://drive.google.com/drive/folders/1XYZ..." \
  jaya

# ✓ Downloaded subtitles to: arc15-jaya/

# Step 3: Match subtitles to videos
uv run match_onepace_subtitles.py "arc15-jaya" "arc15-jaya"

# ✓ Matched and renamed 25 subtitle files

# Step 4: Verify everything
uv run verify_subtitles.py "arc15-jaya"

# Result: 25/25 videos have matching subtitles
# ✓ All videos have matching subtitle files!
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

## Troubleshooting

### Downloads not starting?
- **Check:** `transmission-remote -l` to see transmission status
- **Fix:** Make sure transmission-cli is installed and running

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

- `magnet_downloader.py` - Downloads episodes from nyaa.si
- `download_subtitles.py` - Downloads subtitles from Google Drive
- `match_onepace_subtitles.py` - Renames subtitles to match videos
- `verify_subtitles.py` - Verifies all videos have matching subtitles
- `CLAUDE.md` - This documentation

