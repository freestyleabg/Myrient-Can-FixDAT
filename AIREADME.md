# Myrient Can Fix Dat (MCFD) - Complete Documentation

This document provides comprehensive documentation for the MCFD (Myrient Can Fix Dat) Python script, including user instructions and detailed implementation guide for AI systems.

## Quick Start

### Installation

1. Install Python 3.7+ and required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install requests
   ```

2. Configure the script:
   
   **Myrient URL (required, keeps URL out of GitHub)**:
   ```bash
   # Copy the example file
   cp myrient-base-url.txt.example myrient-base-url.txt
   
   # Edit myrient-base-url.txt and enter your Myrient base URL
   # The file is gitignored and won't be committed to GitHub
   # 
   # The script will automatically normalize the URL:
   # - Adds https:// prefix if missing
   # - Adds trailing / if missing
   # - Strips any path (e.g., /files/Redump/ → base URL only)
   ```
   
   **Other configuration - Edit CONFIG in mcfd.py**:
   - `fixdat`: Path to manual fixdat file (set to `None` to auto-generate)
   - `list_dat`: Path to your filtered DAT file (defaults to latest in `dat_cache/`)
   - `roms_directory`: Directory containing your ROM files
   - `downloads_directory`: Directory where downloads will be saved
   - `igir_exe`: Path to IGIR executable (will be automatically downloaded/updated from GitHub if missing or outdated)
   - `igir_version_override`: Override IGIR version (e.g., `"v4.1.0"` or `"4.1.0"`), set to `None` to use latest version
   - `auto_config_yes`: Set to `True` to automatically answer 'yes' to configuration prompts (download confirmation will still prompt)
   
   **Note**: The `myrient_base_url` must be provided in `myrient-base-url.txt` file. The script will automatically normalize the URL (add https://, trailing /, strip paths). The system-specific URL will be automatically inferred from your DAT file header.

### Usage

Run the script:
```bash
python mcfd.py
```

The script will:
1. Check if a fixdat is set or needs to be generated
2. Validate all configuration paths and URLs
3. Generate a fixdat using IGIR (if needed)
4. Download Myrient directory metadata
5. Match missing games with Myrient files
6. Ask for confirmation before downloading
7. Download missing ROMs with progress feedback

### Features

- Automatically downloads and updates IGIR from GitHub (latest release)
- Uses IGIR to generate fixdats (or uses a manual fixdat)
- Automatically infers Myrient URL from DAT file header
- Validates configuration paths and URLs
- Fetches Myrient directory metadata
- Matches missing games with Myrient files
- Downloads missing ROMs with detailed progress feedback

### How It Works (User Overview)

1. **IGIR Management**: The script automatically:
   - Checks GitHub for the latest IGIR release (or uses version override if set)
   - Downloads IGIR if missing
   - Updates IGIR if a newer version is available (unless version override is set)
   - Tracks installed version to avoid unnecessary updates

2. **Missing Games Identification**: If no manual fixdat is provided, the script identifies missing games using an alternative method:
   - **Note**: Ideally, we should use IGIR's built-in `fixdat` command (see [IGIR Fixdats Documentation](https://igir.io/dats/fixdats/)):
     ```bash
     igir copy zip fixdat --dat <dat> --input <roms> --output <temp> --fixdat
     ```
   - **Current Workaround**: Due to an error in the IGIR executable package (caxa packaging issue causing "cannot find module" errors), we use an alternative method:
     - Running `igir report` to generate a CSV report
     - Filtering the CSV to extract missing games directly
     - Using the missing games list without creating a fixdat file
   - Once the IGIR executable packaging issue is fixed, this will be updated to use the native fixdat command

3. **Myrient URL Inference**: The script automatically determines the correct Myrient URL from your DAT file:
   - Extracts system name from `<header><name>` (e.g., "Sony - PlayStation")
   - Extracts collection type from `<header><url>` (redump.org → Redump, no-intro.org → No-Intro)
   - Builds the full Myrient URL automatically

4. **Myrient Matching**: The script:
   - Fetches the Myrient directory listing
   - Parses filenames, sizes, and URLs
   - Matches game names from the fixdat with Myrient files
   - Handles URL encoding/decoding for special characters

5. **Download**: Downloads missing files with:
   - Per-game progress bars
   - Overall progress tracking
   - Download speed and ETA
   - Summary statistics

### Configuration Notes

- **Fixdat Method**: When no manual fixdat is provided, the script uses an alternative CSV-based method instead of IGIR's native fixdat command due to a packaging issue in the IGIR executable.
- IGIR is automatically downloaded/updated from GitHub releases (no manual download needed)
- Version tracking: The script saves the installed IGIR version and only updates when a newer version is available
- Version override: Set `igir_version_override` in CONFIG to pin a specific IGIR version (useful for compatibility)
- Reports are saved to `reports/` (within the script directory) and kept for reference
- All paths can be relative or absolute
- The script handles URL encoding for special characters in filenames

---

# Implementation Guide for AI Systems

This section provides detailed instructions for recreating or understanding the MCFD (Myrient Can Fix Dat) Python script. It is designed to help advanced AI systems understand the architecture, implementation details, and design decisions.

## Table of Contents

### User Documentation
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [How It Works (User Overview)](#how-it-works-user-overview)
- [Configuration Notes](#configuration-notes)

### Implementation Guide for AI Systems
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Dependencies](#dependencies)
4. [Configuration System](#configuration-system)
5. [Implementation Steps](#implementation-steps)
6. [Key Functions Reference](#key-functions-reference)
7. [Data Flow](#data-flow)
8. [Error Handling](#error-handling)
9. [Future Improvements](#future-improvements)

## Overview

**Purpose**: MCFD is a Python script that identifies missing ROMs from a collection by comparing against a DAT file, then downloads those missing ROMs from Myrient (a ROM hosting service).

**Core Workflow**:
1. Identify missing games (via IGIR report or manual fixdat)
2. Fetch Myrient directory metadata
3. Match missing games with Myrient files
4. Download missing ROMs with progress tracking

**Key Technologies**:
- **IGIR**: ROM collection manager (https://igir.io/) - used to identify missing games
- **Myrient**: ROM hosting service - source for downloads (URL must be provided in myrient-base-url.txt)
- **DAT files**: XML files (Logiqx format) that describe ROM collections
- **Fixdats**: DAT files containing only missing ROMs (see https://igir.io/dats/fixdats/)

## Architecture

### Design Principles

1. **No External Config Files**: All configuration is in-script via a `CONFIG` dictionary
2. **Automatic IGIR Management**: Downloads and updates IGIR from GitHub automatically
3. **Workaround for IGIR Bug**: Uses CSV report method instead of native fixdat command due to packaging issues
4. **Path Resolution**: All relative paths resolve relative to script directory
5. **Progress Feedback**: Real-time progress bars for downloads

### File Structure

```
Myrient-Can-FixDAT/
├── mcfd.py                 # Main script
├── dat/
│   └── psx.dat            # Filtered DAT file (input)
├── roms/                   # ROM collection directory (input)
├── downloads/              # Download destination (output)
├── igir/
│   ├── igir.exe           # IGIR executable (auto-downloaded)
│   └── INSTALLED_VERSION.txt  # Version tracking
```

### External Dependencies

- `reports/` - IGIR CSV reports are saved here (within the script directory)

## Dependencies

### Python Standard Library
- `subprocess` - Running IGIR executable
- `csv` - Parsing IGIR report CSV files
- `urllib.parse` - URL encoding/decoding
- `urllib.request` - Downloading IGIR from GitHub
- `requests` - HTTP requests (Myrient API, file downloads)
- `sys` - System operations
- `re` - Regular expressions (parsing HTML, sizes)
- `json` - GitHub API responses
- `xml.etree.ElementTree` - Parsing DAT files
- `xml.dom.minidom` - XML formatting
- `pathlib.Path` - Path operations
- `collections.Counter` - Extension counting
- `datetime` - Timestamp generation
- `time` - Progress tracking
- `zipfile` - Extracting IGIR releases
- `shutil` - File operations

### External Packages
- `requests` - Must be installed via `pip install requests`

## Configuration System

### CONFIG Dictionary Structure

Located at the top of `mcfd.py`:

```python
CONFIG = {
    "fixdat": None,                    # Path to manual fixdat file (None = auto-generate)
    "list_dat": get_latest_dat_file(), # Latest DAT from dat_cache/
    "roms_directory": r"C:\Users\joemc\Downloads\N64",  # ROM collection directory
    "downloads_directory": r"C:\Users\joemc\Downloads\N64", # Download destination
    "myrient_base_url": load_myrient_base_url(),  # Base Myrient URL (loaded from myrient-base-url.txt, system URL auto-inferred from DAT)
    "igir_exe": "igir/igir.exe",        # IGIR executable path
    "igir_version_override": "4.1.2",   # Pin IGIR version (None = latest)
    "auto_config_yes": True,             # Auto-answer config prompts (download confirmation always prompts)
}
```

**Myrient Base URL Loading** (`load_myrient_base_url()`):
The Myrient base URL must be provided in `myrient-base-url.txt` file. If the file doesn't exist or is empty, the function returns `None` and the script will exit with an error.

The URL is automatically normalized by `load_myrient_base_url()`:
- Adds `https://` prefix if missing (e.g., `myrient.erista.me` → `https://myrient.erista.me/`)
- Adds trailing `/` if missing (e.g., `https://myrient.erista.me` → `https://myrient.erista.me/`)
- Strips any path after domain (e.g., `https://myrient.erista.me/files/Redump/` → `https://myrient.erista.me/`)

The `myrient-base-url.txt` file is gitignored, keeping the URL out of the GitHub repository.

### Path Resolution

All paths are resolved relative to `SCRIPT_DIR` (script's parent directory):
- Relative paths: `"roms"` → `SCRIPT_DIR / "roms"`
- Absolute paths: Unchanged
- Function: `resolve_path(path_str)` handles this

## Implementation Steps

### Step 1: Setup and Imports

1. Import all required standard library modules
2. Define `SCRIPT_DIR = Path(__file__).parent.resolve()`
3. Use Python's `tempfile` module for temporary files (automatically cleaned up by OS)
4. Define IGIR GitHub repository constants:
   - `IGIR_REPO = "emmercm/igir"`
   - `IGIR_RELEASES_API = f"https://api.github.com/repos/{IGIR_REPO}/releases/latest"`
5. Define `CONFIG` dictionary with all configuration options

### Step 2: Utility Functions

Implement these helper functions:

1. **`format_size(size_bytes)`** - Convert bytes to human-readable format (B, KB, MB, GB, TB)
2. **`format_speed(bytes_per_second)`** - Format download speed
3. **`format_time(seconds)`** - Format time (s, m, h)
4. **`parse_size(size_str)`** - Parse size strings like "250.5 MiB" to bytes
5. **`prompt_yes_no(prompt, default='y', skip_auto=False)`** - Interactive prompts with auto-yes support
6. **`resolve_path(path_str)`** - Resolve relative paths to script directory

### Step 3: IGIR Management System

#### 3.1 GitHub API Integration

1. **`get_igir_asset_info(release_data)`**:
   - Extract download URL and asset name from GitHub release JSON
   - Priority: standalone .exe → Windows zip → any .exe → any zip
   - Returns: `(download_url, asset_name)`

2. **`get_latest_igir_version()`**:
   - Fetch from `IGIR_RELEASES_API`
   - Use `get_igir_asset_info()` to find Windows asset
   - Returns: `(version_tag, download_url, asset_name)`

3. **`get_specific_igir_version(version_tag)`**:
   - Fetch specific version: `releases/tags/{version_tag}`
   - Normalize version (add 'v' prefix if missing)
   - Returns: `(version_tag, download_url, asset_name)`

4. **`get_current_igir_version(igir_path)`**:
   - Read from `igir_path.parent / "INSTALLED_VERSION.txt"`
   - Returns version string or None

#### 3.2 Download and Installation

**`download_and_extract_igir(download_url, version_tag, output_path, asset_name, current_version)`**:

1. Determine file type (.exe or .zip) from asset_name
2. Download to temp file
3. If zip: Extract, find `igir.exe`, copy to output
4. If exe: Copy directly to output
5. Set executable permissions (Unix)
6. Save version to `INSTALLED_VERSION.txt`
7. Cleanup temp files
8. Returns: `True` on success

#### 3.3 Update Check Logic

**`check_and_update_igir(igir_path, version_override)`**:

1. If `version_override` provided:
   - Get specific version from GitHub
   - Check if already installed
   - Download if needed
2. Else (use latest):
   - Get latest version
   - Compare with installed version
   - Download/update if newer
3. Returns: `True` if IGIR is ready to use

### Step 4: FixDat Setup

**`check_fixdat_setup()`**:

1. Check if `CONFIG['fixdat']` is set
2. If None:
   - Prompt user (or auto-yes if enabled)
   - Download/update IGIR
   - Return `(True, None)` - will generate later
3. If set:
   - Verify file exists
   - Return `(True, fixdat_path)`
4. Returns: `(success, fixdat_path_or_None)`

### Step 5: Configuration Validation

**`validate_config(has_manual_fixdat)`**:

Validates and prompts for confirmation on:
1. **List DAT file** - Must exist
2. **ROMs directory** - Only if no manual fixdat (needed for IGIR report)
3. **Downloads directory** - Created if missing
4. **Myrient URL** - Automatically inferred from DAT file header (`<name>` and `<url>` tags), then prompts for confirmation

Returns: `(success: bool, myrient_url: str | None)`

All prompts respect `auto_config_yes` setting (except download confirmation).

### Step 6: Missing Games Identification

#### 6.1 IGIR Report Generation

**`run_igir_report(igir_exe, dat_file, rom_dir, output_dir)`**:

1. Verify `igir_exe` exists
2. Generate timestamped CSV filename
3. Build command: `igir report --dat <dat> --input <roms> --report-output <csv>`
4. Run with `subprocess.run(capture_output=False)` for real-time output
5. Verify CSV was created
6. Returns: `Path` to CSV or `None`

**Important**: Reports are saved to `reports/` (within the script directory) and kept.

#### 6.2 Extract Missing Games from CSV

**`get_missing_games_from_report(report_csv)`**:

1. Open CSV with `csv.DictReader`
2. Filter rows where `Status == 'MISSING'`
3. Extract `Game Name` from each row
4. Returns: `list[str]` of game names

#### 6.3 Alternative: Parse Manual FixDat

**`parse_fixdat(fixdat_path, original_dat_path)`**:

1. Parse XML DAT file with `ET.parse()`
2. Find all `<game>` elements
3. Extract `name` attribute from each
4. Count total games in original DAT (if provided) for statistics
5. Display statistics (total, found, missing)
6. Returns: `list[str]` of game names

**Note**: This function is only used when a manual fixdat is provided.

#### 6.4 Main Missing Games Function

**`run_igir_report_and_get_missing_games(igir_exe, dat_file, rom_dir)`**:

**Current Implementation (Workaround)**:
1. Run IGIR report → CSV
2. Extract missing games from CSV
3. Return list of game names

**Ideal Implementation** (when IGIR bug is fixed):
```python
igir copy zip fixdat --dat <dat> --input <roms> --output <temp> --fixdat
```
Then parse the generated fixdat file.

### Step 7: Myrient Metadata Fetching

**`fetch_myrient_index(system_url)`**:

1. Fetch HTML page from Myrient URL with `requests.get()`
2. Parse HTML table rows with regex:
   - Pattern: `r'<tr[^>]*>(.*?)</tr>'`
3. For each row:
   - Extract filename from `<a href="...">` link
   - Extract file size from `<td>` (format: "250.5 MiB")
   - Construct full URL (handle relative/absolute)
   - Store in dict: `{filename: {'size': bytes, 'url': full_url}}`
4. Handle URL encoding/decoding
5. Returns: `dict` mapping filenames to file info

**Key Details**:
- Myrient uses HTML directory listings (not JSON API)
- File sizes are in binary units (MiB, GiB)
- URLs may be relative or absolute
- Multiple filename variations stored (encoded/decoded)
- The `system_url` is automatically inferred from the DAT file header (see `infer_myrient_url_from_dat()`)

**`infer_myrient_url_from_dat(dat_path, base_url)`**:

1. Parse DAT file XML
2. Extract system name from `<header><name>` (e.g., "Sony - PlayStation")
   - Strips common suffixes in parentheses like "(Retool)" or "(No-Intro)"
3. Extract collection type from `<header><url>`:
   - `redump.org` → `/files/Redump`
   - `no-intro.org` → `/files/No-Intro`
4. Build full Myrient URL: `{base_url}/files/{collection}/{url_encoded_system_name}/`
5. Returns: Full Myrient URL or `None` if unable to determine

**Example**:
- DAT with `<name>Sony - PlayStation (Retool)</name>` and `<url>http://redump.org/</url>`
- Base URL: (from `myrient-base-url.txt`)
- Result: `{base_url}/files/Redump/Sony%20-%20PlayStation/`

### Step 8: Game Matching

#### 8.1 Filename Normalization

**`normalize_filename_for_comparison(filename)`**:

Creates a set of filename variations for fuzzy matching:
- Original (lowercase)
- URL-encoded version
- URL-decoded version
- Common URL encoding replacements (%26→&, %20→space, etc.)
- Encoded version of decoded string

Returns: `set` of normalized variations

#### 8.2 Extension Detection

**`find_most_common_extension(myrient_index)`**:

1. Extract extensions from all Myrient filenames
2. Use `Counter` to find most common
3. Default to `.zip` if none found
4. Returns: Extension string (e.g., `".zip"`)

#### 8.3 Matching Logic

**`match_games_with_myrient(games, myrient_index)`**:

1. Find most common extension
2. Build lookup maps:
   - `myrient_lookup`: normalized_variation → file_info
   - `variation_to_filename`: normalized_variation → original_filename
3. For each game:
   - Generate expected filename: `{game_name}{extension}`
   - Generate filename variations
   - Check if any variation exists in lookup
   - If found: Add to matched_games with URL and size
   - If not found: Try matching game name without extension
4. Returns: `list[dict]` with keys: `Game Name`, `Expected Filename`, `Myrient Filename`, `Download URL`, `File Size`

**Performance Optimization**: Uses reverse lookup map to avoid O(n×m) complexity.

### Step 9: Download System

#### 9.1 Progress Bar

**`create_progress_bar(percent, length=50)`**:
- Uses Unicode block characters: `█` (filled) and `░` (empty)
- Returns: String representation

#### 9.2 File Download

**`download_file(url, output_path, expected_size, progress_callback)`**:

1. Start streaming download with `requests.get(stream=True)`
2. Get total size from `Content-Length` header
3. Write chunks to file
4. Update progress every 0.2 seconds:
   - Calculate download rate
   - Calculate ETA
   - Call `progress_callback(downloaded, total, rate, eta)`
5. Returns: `(success, downloaded_bytes, elapsed_time)`

#### 9.3 Batch Download with Progress

**`download_missing_games(matched_games, download_dir)`**:

1. Calculate totals (games, size)
2. Create `ProgressTracker` class for state management
3. For each game:
   - Print game info (name, size)
   - Start download with progress callback
   - Update progress bar in real-time using ANSI escape codes (`\r\033[K`)
   - On completion: Clear line, print result
4. Track: successful, failed, total downloaded, average speed
5. Print final summary

**Progress Display Format**:
```
[1/1792] Game Name                    | Game: 45.2% [█████████░░░░░░░░░░] | Total: 0.3% [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░] | 2.1 GB/692.99 GB @ 5.2 MB/s | ETA: 2h 15m
```

**Key Features**:
- Per-game progress bar
- Overall progress bar
- Download speed and ETA
- Line updates in-place (no newlines)

### Step 10: Main Function Flow

**`main()`**:

1. **Step 1**: Check fixdat setup
   - If no manual fixdat: Download/update IGIR
   
2. **Steps 2-5**: Validate configuration and infer Myrient URL
   - Check all paths exist
   - Infer Myrient URL from DAT file header
   - Prompt for confirmation (respects `auto_config_yes`)
   - Returns inferred `myrient_url`
   
3. **Step 6**: Get missing games
   - If no manual fixdat: Run IGIR report → extract from CSV
   - If manual fixdat: Parse fixdat XML
   
4. **Step 7**: Fetch Myrient metadata
   - Use inferred `myrient_url` from validation step
   - Download and parse directory listing
   
5. **Step 8**: Match games with Myrient
   - Use fuzzy filename matching
   - Handle URL encoding
   
6. **Step 9**: User confirmation
   - Show summary (total missing, available, size)
   - Prompt for download (always prompts, even with `auto_config_yes`)
   
7. **Step 10**: Download files
   - Batch download with progress tracking
   - Show per-game and overall progress

## Key Functions Reference

### Configuration & Setup
- `resolve_path(path_str)` - Resolve relative/absolute paths
- `check_fixdat_setup()` - Determine if fixdat needed
- `validate_config(has_manual_fixdat)` - Validate all config paths

### IGIR Management
- `get_latest_igir_version()` - Get latest from GitHub
- `get_specific_igir_version(version_tag)` - Get specific version
- `check_and_update_igir(igir_path, version_override)` - Main update logic
- `download_and_extract_igir(...)` - Download and install IGIR

### Missing Games Identification
- `run_igir_report(igir_exe, dat_file, rom_dir, output_dir)` - Generate CSV report
- `get_missing_games_from_report(report_csv)` - Extract from CSV
- `parse_fixdat(fixdat_path, original_dat_path)` - Parse manual fixdat
- `count_games_in_dat(dat_path)` - Count total games in DAT
- `run_igir_report_and_get_missing_games(...)` - Main function (workaround method)

### Myrient Integration
- `fetch_myrient_index(system_url)` - Download and parse directory listing
- `parse_size(size_str)` - Parse "250.5 MiB" to bytes

### Matching
- `normalize_filename_for_comparison(filename)` - Create filename variations
- `find_most_common_extension(myrient_index)` - Detect file format
- `match_games_with_myrient(games, myrient_index)` - Match games with files

### Download
- `create_progress_bar(percent, length)` - Generate progress bar string
- `download_file(url, output_path, expected_size, progress_callback)` - Download single file
- `download_missing_games(matched_games, download_dir)` - Batch download with progress

## Data Flow

```
CONFIG Dictionary
    ↓
check_fixdat_setup()
    ├─→ Manual fixdat? → parse_fixdat() → [game names]
    └─→ No fixdat? → run_igir_report() → CSV → get_missing_games_from_report() → [game names]
    ↓
validate_config() → infer_myrient_url_from_dat() → myrient_url
    ↓
[game names] + myrient_url
    ↓
fetch_myrient_index(myrient_url) → {filename: {size, url}}
    ↓
match_games_with_myrient() → [matched games with URLs]
    ↓
User confirmation (always prompts, even with auto_config_yes)
    ↓
download_missing_games() → Download files with progress
```

## Error Handling

### IGIR Execution Errors
- **OSError [WinError 216]**: Executable incompatible → Clear error message
- **subprocess.CalledProcessError**: IGIR command failed → Show output
- **Missing executable**: Check before running, download if needed

### Network Errors
- **requests.exceptions.RequestException**: Timeout/connection errors
- **urllib.error.HTTPError**: GitHub API errors (404 for missing version)
- All network operations have timeouts (60 seconds)

### File Errors
- **ET.ParseError**: Invalid XML in DAT files
- **FileNotFoundError**: Missing config files/directories
- All file operations check existence first

### User Interruption
- **KeyboardInterrupt**: Graceful cleanup, show progress summary

## Future Improvements

### When IGIR Bug is Fixed

Replace `run_igir_report_and_get_missing_games()` with:

```python
def run_igir_fixdat(igir_exe, dat_file, rom_dir, output_path):
    """Use IGIR's native fixdat command."""
    cmd = [
        str(igir_exe),
        "copy", "zip", "fixdat",
        "--dat", str(dat_file),
        "--input", str(rom_dir),
        "--output", str(temp_output_dir),
        "--fixdat-output", str(output_path.parent)
    ]
    subprocess.run(cmd, check=True)
    # Find generated fixdat (timestamped name)
    # Return fixdat path
```

### Potential Enhancements

1. **Resume Downloads**: Check for partial files, resume from last position
2. **Parallel Downloads**: Use threading/async for multiple simultaneous downloads
3. **Retry Logic**: Automatic retry on failed downloads
4. **Rate Limiting**: Respect Myrient rate limits
5. **Checksum Verification**: Verify downloaded files match expected hashes
6. **Database Cache**: Cache Myrient index to avoid re-fetching
7. **Multi-system Support**: Handle multiple systems in one run

## Technical Details

### IGIR Report CSV Format

Columns:
- `Game Name` - Full game name from DAT
- `Status` - "FOUND" or "MISSING"
- `ROM Files` - Path to ROM file (if found)
- Additional metadata columns

### DAT File Format (Logiqx XML)

Structure:
```xml
<?xml version="1.0"?>
<datafile>
    <header>
        <name>Collection Name</name>
        <description>Description</description>
        <!-- ... -->
    </header>
    <game name="Game Name">
        <rom name="rom.bin" size="..." crc="..." md5="..." sha1="..."/>
    </game>
    <!-- ... -->
</datafile>
```

### Myrient HTML Parsing

Myrient uses HTML directory listings. Key patterns:
- Table rows: `<tr>...</tr>`
- File links: `<a href="filename.zip">filename.zip</a>`
- File sizes: `<td>250.5 MiB</td>`

### URL Encoding Handling

Special characters in filenames:
- Spaces: `%20` or `+`
- Ampersand: `%26` or `&`
- Parentheses: `%28`, `%29` or `(`, `)`
- Apostrophe: `%27` or `'`

The matching system handles all variations.

### Progress Bar Implementation

- Uses ANSI escape code `\033[K` to clear line
- `\r` to return to start of line
- `end=''` and `flush=True` for real-time updates
- Updates every 0.2 seconds for smooth animation

## Testing Considerations

When recreating this script, test:

1. **IGIR Download**: Various architectures (x64, arm64, etc.)
2. **IGIR Versions**: Latest and pinned versions
3. **Path Resolution**: Relative and absolute paths
4. **Myrient Parsing**: Various HTML structures
5. **Filename Matching**: Special characters, URL encoding
6. **Download Progress**: Large files, slow connections
7. **Error Recovery**: Network failures, interrupted downloads
8. **Edge Cases**: Empty collections, no missing games, all missing

## References

- [IGIR Documentation](https://igir.io/)
- [IGIR Fixdats Documentation](https://igir.io/dats/fixdats/)
- [IGIR GitHub Repository](https://github.com/emmercm/igir)
- [Myrient](https://myrient.erista.me/) (URL must be provided in myrient-base-url.txt)
- [Logiqx DAT Format](https://www.logiqx.com/DatFAQs/)

## Code Organization

The script is organized into logical sections:

1. **Configuration** (lines ~28-46): Constants and CONFIG
2. **Utility Functions** (lines ~48-153): Helpers (formatting, prompts, paths)
3. **IGIR Management** (lines ~156-431): Download, update, version tracking
4. **FixDat Setup** (lines ~434-465): Check if fixdat needed
5. **Config Validation** (lines ~468-513): Validate all paths
6. **IGIR Report** (lines ~516-577): Generate CSV reports
7. **Missing Games** (lines ~580-659): Extract from CSV or parse fixdat
8. **Myrient Integration** (lines ~662-752): Fetch and parse directory
9. **Matching** (lines ~755-928): Match games with Myrient files
10. **Download** (lines ~931-1107): Download with progress
11. **Main** (lines ~1110-1229): Orchestrate all steps

Each section is clearly marked with comment headers using `"=" * 60`.

