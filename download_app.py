import threading
import yt_dlp
import flet as ft
import tkinter as tk
from tkinter import filedialog


def pick_folder(output_dir: ft.TextField, page: ft.Page):
    # Use tkinter folder dialog and bring it to front
    root = tk.Tk()
    root.withdraw()
    # Ensure dialog is topmost
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(parent=root)
    root.destroy()
    if folder:
        output_dir.value = folder
        page.update()


def main(page: ft.Page):
    page.title = "YouTube Downloader"
    page.window_width = 600
    page.window_height = 540

    # URL input
    url_field = ft.TextField(
        label="YouTube URL",
        hint_text="Enter video or playlist URL",
        expand=True,
    )

    # Output directory display
    output_dir = ft.TextField(
        label="Output Directory",
        hint_text="Select folder...",
        expand=True,
        read_only=True,
    )
    pick_button = ft.ElevatedButton(
        text="Browse...",
        on_click=lambda e: pick_folder(output_dir, page),
    )

    # Resolution selection
    resolution_dropdown = ft.Dropdown(
        label="Resolution:",
        width=150,
        options=[
            ft.dropdown.Option("Highest", "best"),
            ft.dropdown.Option("360p", "360"),
            ft.dropdown.Option("480p", "480"),
            ft.dropdown.Option("720p", "720"),
            ft.dropdown.Option("1080p", "1080"),
            ft.dropdown.Option("4K", "2160"),
        ],
        value="1080",
    )
    disclaimer = ft.Text(
        "⚠️ 4K downloads may need extra codecs and could skip audio.",
        color="red",
        visible=False,
    )

    # Format selection
    format_radios = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(label="MP4 only", value="mp4"),
            ft.Radio(label="MP3 only", value="mp3"),
            ft.Radio(label="Both",    value="both"),
        ], spacing=5),
        value="mp4",
    )

    # Logs area
    log_area = ft.TextField(
        label="Logs",
        multiline=True,
        expand=True,
        read_only=True,
    )

    # Show disclaimer if 4K selected
    def on_resolution_change(e):
        disclaimer.visible = (resolution_dropdown.value == "2160")
        page.update()
    resolution_dropdown.on_change = on_resolution_change

    # Download handler
    def start_download(e):
        url = url_field.value.strip()
        out_dir = output_dir.value.strip() or "."
        choice = format_radios.value
        res = resolution_dropdown.value
        if not url:
            log_area.value += "❌ Please enter a valid URL\n"
            page.update()
            return

        # Warn for high res
        if res == "2160":
            log_area.value += "⚠️ Attempting 4K download; audio may require conversion.\n"

        def progress_hook(d):
            status = d.get('status')
            if status == 'downloading':
                log_area.value += f"⬇️ {d.get('_percent_str')} at {d.get('_speed_str')}\n"
            elif status == 'finished':
                log_area.value += "✅ Download finished\n"
            page.update()

        def download_task():
            tasks = []
            # MP4 task with re-encoding for compatibility
            if choice in ("mp4", "both"):
                if res == "best":
                    fmt = "bestvideo+bestaudio/best"
                else:
                    fmt = f"bv*[height<={res}]+ba/best"
                tasks.append({
                    "format": fmt,
                    "outtmpl": f"{out_dir}/%(title)s.mp4",
                    "recode_video": "mp4",
                    "progress_hooks": [progress_hook],
                })
            # MP3 task
            if choice in ("mp3", "both"):
                tasks.append({
                    "format": "bestaudio/best",
                    "outtmpl": f"{out_dir}/%(title)s.mp3",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                    "progress_hooks": [progress_hook],
                })

            for opts in tasks:
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([url])
                except Exception as err:
                    log_area.value += f"❌ Error: {err}\n"
            log_area.value += "🎉 All done!\n"
            page.update()

        threading.Thread(target=download_task, daemon=True).start()
        log_area.value += "🚀 Starting download...\n"
        page.update()

    # Download button
    download_btn = ft.ElevatedButton(
        text="Download",
        icon=ft.Icons.FILE_DOWNLOAD,
        on_click=start_download,
    )

    # Layout
    page.add(
        url_field,
        ft.Row([output_dir, pick_button], spacing=10),
        ft.Row([resolution_dropdown, disclaimer], spacing=10),
        ft.Row([ft.Text("Format:"), format_radios], spacing=10),
        download_btn,
        log_area,
    )


if __name__ == "__main__":
    ft.app(target=main)