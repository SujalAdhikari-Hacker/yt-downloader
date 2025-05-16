# YouTubeDownloader

A **standalone** Windows application for downloading YouTube videos and audio, built with **Python**, **Flet**, and **yt-dlp**, and packaged with **PyInstaller**. Beginners can run the `.exe` directly—no Python setup required—while advanced users can customize or extend the source code.

---

## 🚀 Features

* **User-friendly GUI** with URL input, folder picker, resolution & format selectors.
* **Resolution options**: Highest, 360p, 480p, 720p, 1080p, and 4K (with disclaimer).
* **Format choices**: MP4 only, MP3 only, or both in one click.
* **Integrated FFmpeg** for merging/re-encoding and extracting audio.
* **Standalone EXE**: no external dependencies or Python install needed.
* **Open source**: Easily modify, extend, or repackage.

---

## 📂 Repository Structure

```text
YT_DOWNLOADER/
├─ download_app.py        # Main script with Flet GUI logic
├─ ffmpeg.exe             # Bundled FFmpeg binary for merging audio/video
├─ YouTubeDownloader.exe  # Standalone Windows application (in dist/)
├─ dist/                  # PyInstaller output directory
│  └─ YouTubeDownloader.exe
├─ build/                 # PyInstaller build artifacts
├─ README.md              # You are here
└─ LICENSE                # Project license
```

---

## 🔧 Requirements (for source-based usage)

* **Python 3.7+**
* **pip** package manager
* **Windows 10+**
* **FFmpeg** (if running from source; included in the EXE build)

### Python Dependencies

```bash
pip install yt-dlp flet
```

---

## ⚙️ Installation & Usage

### 📦 Run the Standalone EXE (Recommended)

1. Download `YouTubeDownloader.exe` from the [dist folder](dist/).
2. Double-click to launch—no Python, no setup.
3. Enter the YouTube URL, pick an output folder, select resolution & format, and click **Download**.

### 🐍 Run from Source (Advanced)

```bash
# Clone the repo
git clone https://github.com/YourUserName/YT_DOWNLOADER.git
cd YT_DOWNLOADER/New\ folder

# Install dependencies
pip install yt-dlp flet
# Ensure ffmpeg.exe is in the same folder or on your PATH

# Launch
python download_app.py
```

---

## 🖼️ Packaging with PyInstaller (for Developers)

To rebuild the standalone EXE:

```bash
# Clean previous builds
rmdir /S /Q build dist
del YouTubeDownloader.spec

# Bundle into single EXE
py -3 -m PyInstaller --clean \
  --onefile \
  --windowed \
  --name YouTubeDownloader \
  --add-binary "ffmpeg.exe;." \
  download_app.py
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

* Report issues or request features via [GitHub Issues](https://github.com/YourUserName/YT_DOWNLOADER/issues).
* Fork, improve, and submit PRs.
* Suggest UI/UX enhancements or additional download options.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
