# Myrient Can FixDAT

A GUI tool that downloads missing ROMs from Myrient to complete your game collection. Point it at your existing ROMs, give it a DAT file describing your desired collection, and it will download only what you're missing.

![Screenshot placeholder](https://via.placeholder.com/800x500?text=Screenshot+Coming+Soon)

## Features

- **Smart Downloads** — Only downloads what you're missing, not your entire collection
- **1G1R DAT Support** — Works with filtered DAT files for curated "One Game, One ROM" collections
- **Built-in DAT Downloader** — Download fresh 1G1R DATs directly from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R)
- **IGIR Integration** — Optionally use [IGIR](https://github.com/emmercm/igir) to scan your existing collection
- **Progress Tracking** — Real-time download progress, speed, and ETA
- **Dark Mode UI** — Modern, easy-on-the-eyes interface

---

## Getting Started

### Option 1: Standalone Executable (Recommended)

1. Download `MyrientCanFixDAT.exe` from the [Releases](https://github.com/UnluckyForSome/Myrient-Can-FixDAT/releases) page
2. Run the `.exe` — no installation required
3. Configure your paths and click **Run**

### Option 2: Run from Python

If you prefer running from source:

```bash
# Clone the repository
git clone https://github.com/UnluckyForSome/Myrient-Can-FixDAT.git
cd Myrient-Can-FixDAT

# Install dependencies
pip install -r requirements.txt

# Run the application
python MyrientCanFixDAT.py
```

**Requirements:** Python 3.7+ with PyQt5, requests, and lxml.

---

## Configuration Guide

### Paths Section

| Field | Description |
|-------|-------------|
| **DAT File** | The DAT file describing your desired collection. This defines which games you want. Use "Download 1G1R" to fetch a pre-filtered DAT, or browse to your own. |
| **ROMs Directory** | Where your current ROM collection is stored. Only needed if using IGIR to scan existing ROMs. |
| **Downloads Directory** | Where new downloads will be saved. Can be the same as your ROMs directory. |
| **Myrient Base URL** | The base URL for Myrient (a ROM hosting service). The system-specific path is automatically determined from your DAT file. |

### Options Section

| Option | Description |
|--------|-------------|
| **Use IGIR to Align a Pre-Existing Collection** | Enable this if you already have some ROMs and only want to download what's missing. When enabled, the tool will use [IGIR](https://github.com/emmercm/igir) to scan your ROMs directory and compare it against the DAT file. IGIR is automatically downloaded if needed. |
| **Move Unrequired ROMs** | When enabled, ROMs in your collection that aren't in the DAT file will be moved to a separate folder. Useful for cleaning up duplicates or unwanted versions. |

---

## Downloading DAT Files

Click the **"Download 1G1R"** button to open the DAT downloader. This fetches fresh, daily-updated 1G1R (One Game, One ROM) DAT files from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R).

### What is 1G1R?

1G1R DAT files are filtered versions of full DAT collections (like Redump or No-Intro) that include only one version of each game — typically the best regional release. This gives you a curated collection without duplicates.

### Available Collections

When downloading, you can choose from:

**Virgin DAT Source:**
- **Redump** — Disc-based systems (PlayStation, Saturn, Dreamcast, etc.)
- **No-Intro** — Cartridge-based systems (NES, SNES, Game Boy, N64, etc.)

**Filtered Game Collection:**
- **McLean** — English-only retail releases. The leanest option.
- **PropeR** — All languages, includes add-ons, educational, and promotional content.
- **Hearto** — Most inclusive: retail, unlicensed, demos, and preproduction (betas/protos).

After selecting your source and collection type, choose the system you want (e.g., "Sony - PlayStation") and click Download.

> **Note:** DAT files are updated daily by [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R), so you can always get the latest curated collections.

---

## Typical Workflow

### Starting a New Collection

1. Click **"Download 1G1R"** and select your system and preferred collection (e.g., McLean for English-only)
2. Set your **Downloads Directory** to where you want your ROMs saved
3. Enter the **Myrient Base URL**
4. Leave "Use IGIR" **unchecked** (you don't have existing ROMs to scan)
5. Click **Run** to download your entire collection

### Updating an Existing Collection

1. Click **"Download 1G1R"** to get the latest DAT for your system
2. Set **ROMs Directory** to your existing collection
3. Set **Downloads Directory** (can be the same as ROMs, or a separate folder)
4. **Check** "Use IGIR to Align a Pre-Existing Collection"
5. Click **Run** — only missing games will be downloaded

### Cleaning Up Duplicates

1. Load a 1G1R DAT file for your system
2. Set **ROMs Directory** to your collection
3. **Check** "Move Unrequired ROMs"
4. Click **Run** — ROMs not in the DAT will be moved to a `_moved` subfolder

---

## How It Works

1. **Parse DAT** — Reads the DAT file to understand your desired collection
2. **Scan ROMs** (if IGIR enabled) — Compares your existing ROMs against the DAT
3. **Fetch Myrient Index** — Downloads the file listing from Myrient for your system
4. **Match Missing Games** — Identifies which games you need and finds them on Myrient
5. **Download** — Downloads missing files with progress tracking

The Myrient URL is automatically constructed from your DAT file's header information (system name and source), so you only need to provide the base URL.

---

## Troubleshooting

### "DAT file not found"
Make sure you've either downloaded a DAT using the built-in downloader or browsed to a valid `.dat` file.

### "Could not connect to Myrient"
Check that your Myrient Base URL is correct and that you have internet access. The URL should be just the base domain without any path.

### "IGIR failed to run"
IGIR is automatically downloaded from GitHub. If it fails, check your internet connection. The tool will retry on the next run.

### Downloads are slow
Download speeds depend on Myrient's servers and your connection. The tool shows real-time speed and ETA so you can monitor progress.

---

## Credits

- [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) — Daily updated 1G1R DAT files
- [IGIR](https://github.com/emmercm/igir) — ROM collection manager by emmercm
- [Retool](https://github.com/unexpectedpanda/retool) — 1G1R filtering tool by unexpectedpanda
- [Redump](http://redump.org/) — Disc preservation project
- [No-Intro](https://no-intro.org/) — Cartridge preservation project

---

## License

This project is provided as-is for personal use. Please respect the terms of service of any sites you interact with.
