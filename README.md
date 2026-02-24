# 🎮 Can FixDAT

**Version: 1.1.0**

A GUI tool that downloads missing ROMs from Myrient to complete your game collection. Point it at your existing ROMs, give it a DAT file describing your desired collection, and it will download only what you're missing. Includes built-in DAT downloaders for daily [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) 1G1R sets and [RetroAchievements](https://github.com/UltraGodAzgorath/Unofficial-RA-DATs) DATs.

![Can FixDAT Screenshot](.github/MyrientCanFixDat.PNG)

## ✨ Features

- 🧠 **Smart Downloads** — Only downloads what you're missing, using either [IGIR](https://github.com/emmercm/igir) for full validation or without, using simple name matching.
- 📋 **No-Intro and Redump DAT Support** — Works with any No-Intro or Redump DAT files.
- 📥 **Built-in DAT Downloaders** — Download DATs from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) (1G1R sets) or [RetroAchievements](https://github.com/UltraGodAzgorath/Unofficial-RA-DATs) (unofficial RA DATs) with one click.
- 🔧 **IGIR Integration** — Optionally use [IGIR](https://github.com/emmercm/igir) to scan your existing collection to ensure a perfect set of games every time.

## 🚀 Getting Started

### Option 1: Standalone Executable

For convenience, a prebuilt [`CanFixDAT.exe`](https://github.com/UnluckyForSome/Myrient-Can-FixDAT/releases/latest/download/CanFixDAT.exe) is provided in the Releases section. It is generated directly from this repository's Python source using PyInstaller, which bundles the app and Python runtime into a single executable.

🔍 You can review the source used to build the executable here: [`MyrientCanFixDAT.py`](https://github.com/UnluckyForSome/Myrient-Can-FixDAT/blob/main/MyrientCanFixDAT.py).


**Steps:**
1. 📦 Download [`CanFixDAT.exe`](https://github.com/UnluckyForSome/Myrient-Can-FixDAT/releases/latest/download/CanFixDAT.exe) from the **Releases** page  
2. ▶️ Run the `.exe` — required directories will be created alongside it  
3. ⚙️ Configure your paths and click **Run**

### Option 2: Run from Python 🐍

If you prefer more transparency and running from source:

```bash
# Clone the repository
git clone https://github.com/UnluckyForSome/Myrient-Can-FixDAT.git
cd Myrient-Can-FixDAT

# Install dependencies
pip install PyQt5 requests lxml

# Run the application
python MyrientCanFixDAT.py
```

**Requirements:** Python 3.7+

---

## ⚙️ Configuration Guide

### 📂 Paths Section

**📄 DAT File**  
The DAT file defines the collection you want to build. This tells the tool which games should exist in your final set.  
You can either:
- Click **Fresh 1G1R** to fetch a pre-filtered 1G1R DAT from **Fresh1G1R**,
- Click **RetroAchievements** to fetch a DAT from the **Unofficial RetroAchievements DATs** repo, or
- Click **Browse** to choose your own No-Intro or Redump DAT file

**📁 ROMs Directory**  
The folder containing your existing ROM collection.  
This is only required if you enable **Use IGIR**, which scans your current files to determine what's missing.

**💾 Downloads Directory**  
Where newly downloaded ROMs will be saved.  
This can be the same as your ROMs directory or a separate folder if you prefer to stage downloads first.

**🌐 Myrient Base URL**  
Myrient is not hardcoded in the app; you provide your own Myrient base URL here.  
The system-specific path each set of downloads is automatically determined from the DAT file, so only the base URL is required.

---

### 🎛️ Options Section

**🔧 Use IGIR to Align a Pre-Existing Collection**  
Enable this if you already have ROMs and only want to download what's missing.  
When enabled, the tool uses IGIR to scan your ROMs directory and compare it against the DAT file.  

The IGIR .exe will be downloaded automatically if it isn't already present, so ensure you're OK with this before proceeding.

**🧹 Move Unrequired ROMs**  
When enabled, any ROMs in your collection that are *not* listed in the DAT file will be moved to a separate `NotRequired` folder. **This doesn't delete anything**, instead it just moved the potentially unwanted ROMs to a separate folder allowing you to decide what to delete at a later date.  

This is useful for cleaning up duplicates or unwanted versions while keeping them safely out of the way.

---

## 📥 Downloading DAT Files

The app offers two built-in DAT sources next to the DAT file field:

### Fresh 1G1R

Click **Fresh 1G1R** to open the 1G1R DAT downloader. You can fetch fresh, daily-updated 1G1R (One Game, One ROM) DAT files from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R).

**What is 1G1R?**  
1G1R DAT files are filtered versions of full DAT collections (like Redump or No-Intro) that include only one version of each game — typically the best regional release. This gives you a curated collection without duplicates.

**Virgin DAT Source:**
- 💿 **Redump** — Disc-based systems (PlayStation, Saturn, Dreamcast, etc.)
- 🎮 **No-Intro** — Cartridge-based systems (NES, SNES, Game Boy, N64, etc.)

**Filtered Game Collection:**
- 🧼 **McLean** — English-only retail releases. The leanest option.
- 📦 **PropeR** — All languages, includes add-ons, educational, and promotional content.
- ❤️ **Hearto** — Most inclusive: retail, unlicensed, demos, and preproduction (betas/protos).

Pick your source and collection type, choose the system (e.g., "Sony - PlayStation"), then click Download.

### RetroAchievements

Click **RetroAchievements** to open a separate dialog that lists DAT files from the [Unofficial RetroAchievements DATs](https://github.com/UltraGodAzgorath/Unofficial-RA-DATs) repository. These DATs are aligned with [RetroAchievements](https://retroachievements.org/) sets (No Subfolders). Pick a system DAT and click Download. The app has no control over this repo — DATs may be out of date or unsuitable; use at your discretion.

## 🙏 Thanks

- [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) — Daily updated 1G1R DAT files
- [Unofficial RetroAchievements DATs](https://github.com/UltraGodAzgorath/Unofficial-RA-DATs) — RetroAchievements-aligned DAT sets
- [IGIR](https://github.com/emmercm/igir) — ROM collection manager by emmercm
- [Retool](https://github.com/unexpectedpanda/retool) — 1G1R filtering tool by unexpectedpanda
- [Redump](http://redump.org/) — Disc preservation project
- [No-Intro](https://no-intro.org/) — Cartridge preservation project

---

## ESDE ROM Formatter (New)

This repo now includes:
- `esde_rom_formatter_gui.py` (GUI app)
- `esde_rom_formatter_core.py` (CLI/core engine)

Which one to run:
- Use `esde_rom_formatter_gui.py` for normal use (GUI window).
- Use `esde_rom_formatter_core.py` only if you want command-line usage or scripting.

It handles ES-DE multi-disc setups using the **directories interpreted as files** layout.

What it does:
- Scans a ROM folder for multi-disc naming patterns like `(Disc 1)`, `(Disk 2)`, `CD1`, etc.
- Creates a folder named `<Game>.m3u`
- Moves matching disc files into that folder
- Creates `<Game>.m3u` playlist inside that folder
- Prefers `.cue` entries in the playlist when available (best for BIN/CUE sets)
- Uses extension-agnostic scanning so ES-DE-supported formats (including `.rvz`, `.wbfs`, `.wia`, etc.) are detected without hardcoded per-system lists

Run GUI:

```bash
python esde_rom_formatter_gui.py
```

CLI examples:

```bash
python esde_rom_formatter_core.py "D:\Roms\psx" --recursive --dry-run
python esde_rom_formatter_core.py "D:\Roms\psx" --recursive
python esde_rom_formatter_core.py --pick-folder --recursive
python esde_rom_formatter_core.py "D:\Roms\psx" --extract-archives --postprocess-single-disc --delete-archives
```

GUI options now include:
- Extract `.zip/.7z` archives first
- Delete archives after successful extraction
- Post-process single-disc folders (e.g. `Game` -> `Game.cue`)

Build as `.exe` (PyInstaller):

```bash
pip install PyQt5 pyinstaller
pyinstaller --onefile --windowed --name ESDE-ROM-Formatter esde_rom_formatter_gui.py
```
