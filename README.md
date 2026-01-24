# 🎮 Myrient Can FixDAT

A GUI tool that downloads missing ROMs from Myrient to complete your game collection. Point it at your existing ROMs, give it a DAT file describing your desired collection, and it will download only what you're missing. Includes automatic download of the latest daily [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) DATs.

![Myrient Can FixDAT Screenshot](.github/MyrientCanFixDat.PNG)

## ✨ Features

- 🧠 **Smart Downloads** — Only downloads what you're missing, using either [IGIR](https://github.com/emmercm/igir) for full validation or without, using simple name matching.
- 📋 **No-Intro and Redump DAT Support** — Works with any No-Intro or Redump DAT files.
- 📥 **Built-in DAT Downloader** — Download fresh 1G1R DATs directly from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) to ensure you're getting the latest 1G1R sets.
- 🔧 **IGIR Integration** — Optionally use [IGIR](https://github.com/emmercm/igir) to scan your existing collection to ensure a perfect set of games every time.

---

## 🚀 Getting Started

### Option 1: Standalone Executable

> ⚠️ As a general rule, you should **never blindly run `.exe` files from GitHub (or anywhere else)**. Only run executables if you trust the source and understand the risks.

For convenience, a prebuilt `MyrientCanFixDAT.exe` is provided in the Releases section. It is **generated directly from this repository's Python source using PyInstaller**, which bundles the app and Python runtime into a single executable.

🔍 You can review the source used to build the executable here: [`MyrientCanFixDAT.py`](https://github.com/UnluckyForSome/Myrient-Can-FixDAT/blob/main/MyrientCanFixDAT.py).

**Steps:**
1. 📦 Download `MyrientCanFixDAT.exe` from the **Releases** page  
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
- Click **Download 1G1R** to fetch a pre-filtered 1G1R DAT from **Fresh1G1R**, or
- Browse to your own No-Intro or Redump DAT file

**📁 ROMs Directory**  
The folder containing your existing ROM collection.  
This is only required if you enable **Use IGIR**, which scans your current files to determine what's missing.

**💾 Downloads Directory**  
Where newly downloaded ROMs will be saved.  
This can be the same as your ROMs directory or a separate folder if you prefer to stage downloads first.

**🌐 Myrient Base URL**  
The base URL for Myrient. It's not coded into this repo, you have to add it yourself!  
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

Clicking the **"Download 1G1R"** button opens up the DAT downloader. This allows the user to fetch fresh, daily-updated 1G1R (One Game, One ROM) DAT files from [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R).

### ❓ What is 1G1R?

1G1R DAT files are filtered versions of full DAT collections (like Redump or No-Intro) that include only one version of each game — typically the best regional release. This gives you a curated collection without duplicates.

### 📚 Available Collections

 DAT files are updated daily by [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R), so you can always get the latest curated collections. When downloading from Fresh1G1R, first pick the "Virgin DAT Source" - then, pick your preferred filtered game collection:

**Virgin DAT Source:**
- 💿 **Redump** — Disc-based systems (PlayStation, Saturn, Dreamcast, etc.)
- 🎮 **No-Intro** — Cartridge-based systems (NES, SNES, Game Boy, N64, etc.)


**Filtered Game Collection:**
- 🧼 **McLean** — English-only retail releases. The leanest option.
- 📦 **PropeR** — All languages, includes add-ons, educational, and promotional content.
- ❤️ **Hearto** — Most inclusive: retail, unlicensed, demos, and preproduction (betas/protos).

After selecting your source and collection type, choose the system you want (e.g., "Sony - PlayStation") and click Download.

## 🙏 Thanks

- [Fresh1G1R](https://github.com/UnluckyForSome/Fresh1G1R) — Daily updated 1G1R DAT files
- [IGIR](https://github.com/emmercm/igir) — ROM collection manager by emmercm
- [Retool](https://github.com/unexpectedpanda/retool) — 1G1R filtering tool by unexpectedpanda
- [Redump](http://redump.org/) — Disc preservation project
- [No-Intro](https://no-intro.org/) — Cartridge preservation project

---