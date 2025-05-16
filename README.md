# YouTubeDownloader

> **My personal Windows app** for downloading YouTube videos and audio, built entirely in Python using Flet and yt-dlp, then packaged into a single `.exe` with PyInstaller.

---

## 🚀 About This Project

> **Note:** Pre-built `YouTubeDownloader.exe` and `ffmpeg.exe` are not included in this repository due to GitHub file size limits. You can either download them from the project’s Releases page (when available), or generate your own binaries following the Packaging instructions below.

I created **YouTubeDownloader** to have a simple, no-fuss desktop tool:

* Intuitive GUI: paste URL, pick folder, choose resolution & format.
* Supports resolutions up to 4K, with automatic audio merging and re-encoding.
* Export to MP4, MP3, or both in one click.
* Packaged as a **standalone EXE**—no Python install required.

This is my fully open-source side project; feel free to explore or tweak how I did it.

---

## 🔧 Quick Start

### 📦 Run the EXE (zero setup)

> YouTubeDownloader.exe and ffmpeg.exe aren’t stored here due to size constraints. To get a ready-to-run EXE, either:
>
> 1. Download the latest release from the GitHub Releases page (when available).
> 2. Build your own using PyInstaller (see the **Packaging** section below).

### 🐍 Run from Source (for tinkers)

```bash
# Clone or download this repo
cd YT_DOWNLOADER

# Install dependencies (Python 3.7+ required)
pip install yt-dlp flet
# Ensure ffmpeg.exe sits alongside download_app.py or is on your PATH

# Start the app
git download_app.py
```

---

## ⚙️ How I Packaged the EXE

I use **PyInstaller** to bundle everything into one file:

```bash
# Clean old builds
del YouTubeDownloader.spec
rmdir /S /Q build dist

# Create the EXE
py -3 -m PyInstaller --clean \
  --onefile \
  --windowed \
  --name YouTubeDownloader \
  --add-binary "ffmpeg.exe;." \
  download_app.py
```

This embeds Python, Flet, yt-dlp, and FFmpeg so you don’t need any external installs.

---

## 📚 Educational Use Only

This tool is provided solely for educational purposes and personal learning. Downloading copyrighted content may violate YouTube's Terms of Service and local laws. Use responsibly and at your own risk.
