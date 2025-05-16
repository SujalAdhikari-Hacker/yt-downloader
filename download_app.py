import threading
import yt_dlp
import flet as ft
import tkinter as tk
from tkinter import filedialog
import re
import os
import json
import shutil
import traceback
import string

# Settings
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".yt_downloader_settings.json")
RETRY_COUNT = 3
stop_event = threading.Event()

# --- Utility Functions ---
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception:
        pass


def sanitize_filename(name: str) -> str:
    allowed = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in allowed).strip()


def pick_folder(output_field: ft.TextField, page: ft.Page, settings: dict):
    root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
    folder = filedialog.askdirectory(parent=root);
    root.destroy()
    if folder:
        output_field.value = folder
        settings['last_folder'] = folder
        save_settings(settings)
        page.snack_bar = ft.SnackBar(ft.Text(f"Selected folder: {folder}"))
        page.snack_bar.open = True
        page.update()

# --- Main App ---
def main(page: ft.Page):
    settings = load_settings()
    page.title = "YouTube Downloader"
    page.window_width = 600
    page.window_height = 800
    page.window_center = True

    # URL input
    url_field = ft.TextField(label="YouTube URL(s)", hint_text="Enter one URL per line", expand=True)
    paste_btn = ft.IconButton(
        icon=ft.Icons.CONTENT_PASTE,
        tooltip="Paste URLs",
        on_click=lambda e: (setattr(url_field, 'value', page.get_clipboard()), page.update())
    )
    # Drag & Drop support using on_file_drop
    def handle_drop(e):
        urls = []
        if getattr(e, 'files', None):
            urls = [f.path for f in e.files]
        elif getattr(e, 'data', None):
            urls = e.data.splitlines()
        if urls:
            url_field.value = '\n'.join(urls)
            page.update()
    page.on_file_drop = handle_drop

    url_row = ft.Row([url_field, paste_btn], spacing=5)

    # Output dir
    default_folder = settings.get('last_folder', os.getcwd())
    output_field = ft.TextField(label="Output Directory", value=default_folder, expand=True)
    browse_btn = ft.ElevatedButton(text="Browse...", on_click=lambda e: pick_folder(output_field, page, settings))
    out_row = ft.Row([output_field, browse_btn], spacing=5)

    # Resolution
    resolution = ft.Dropdown(
        options=[
            ft.dropdown.Option("best", "Highest"),
            ft.dropdown.Option("360",  "360p"),
            ft.dropdown.Option("480",  "480p"),
            ft.dropdown.Option("720",  "720p"),
            ft.dropdown.Option("1080", "1080p"),
            ft.dropdown.Option("2160", "4K"),
        ],
        value=settings.get('resolution', 'best'),
        width=150
    )
    disclaimer = ft.Text("⚠️ 4K may skip audio or need extra codecs.", color="red", visible=False)
    def on_res_change(e):
        disclaimer.visible = (resolution.value == "2160")
        settings['resolution'] = resolution.value; save_settings(settings); page.update()
    resolution.on_change = on_res_change
    res_row = ft.Row([resolution, disclaimer], spacing=5)

    # Format radios
    fmt_radios = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(label="MP4", value="mp4"),
            ft.Radio(label="MP3", value="mp3"),
            ft.Radio(label="Both", value="both"),
        ], spacing=20),
        value=settings.get('format', 'mp4')
    )
    fmt_radios.on_change = lambda e: (settings.update({'format': fmt_radios.value}), save_settings(settings))

    # Checkboxes
    subs_cb = ft.Checkbox(label="Download subtitles", value=settings.get('subtitles', False), on_change=lambda e: (settings.update({'subtitles': subs_cb.value}), save_settings(settings)))
    exit_cb = ft.Checkbox(label="Auto-exit after download", value=settings.get('auto_exit', False), on_change=lambda e: (settings.update({'auto_exit': exit_cb.value}), save_settings(settings)))

    # Buttons
    download_btn = ft.ElevatedButton(text="Download", icon=ft.Icons.FILE_DOWNLOAD)
    stop_btn     = ft.ElevatedButton(text="Stop",     icon=ft.Icons.STOP, disabled=True)

    # Progress & logs
    progress = ft.ProgressBar(width=400)
    log_area = ft.TextField(label="Logs", multiline=True, read_only=True, expand=True, height=200)
    clear_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Clear logs", on_click=lambda e: (setattr(log_area, 'value', ''), page.update()))
    log_section = ft.Column([log_area, clear_btn])

    page.add(url_row, out_row, res_row, fmt_radios, subs_cb, exit_cb,
             ft.Row([download_btn, stop_btn], spacing=20), progress, log_section)

    def start_download(e):
        stop_event.clear()
        download_btn.disabled = True; stop_btn.disabled = False; log_area.value = ''; progress.value = 0; page.update()

        urls = [u.strip() for u in url_field.value.splitlines() if u.strip()]
        if not urls:
            log_area.value = '❌ No URLs entered'; download_btn.disabled = False; stop_btn.disabled = True; page.update(); return

        # Validate URLs
        pat = re.compile(r'^https?://(www\.)?(youtube\.com|youtu\.be)/')
        for u in urls:
            if not pat.match(u):
                log_area.value = f'❌ Invalid URL: {u}'; download_btn.disabled = False; stop_btn.disabled = True; page.update(); return

        # FFmpeg check
        choice = fmt_radios.value
        if choice in ('mp3', 'both') and not shutil.which('ffmpeg'):
            log_area.value += '\n⚠️ ffmpeg not found; mp3 may fail'
            page.update()

        # Build opts_list
        is_playlist  = 'list=' in urls[0]
        base_pat     = '%(playlist_index)s - %(title)s' if is_playlist else '%(title)s'
        filename_tmplt = os.path.join(output_field.value, f"{base_pat}.%(ext)s")
        opts_list.clear()
        if choice in ('mp4','both'):
            fstr = 'bestvideo+bestaudio/best' if resolution.value=='best' else f'bv*[height<={resolution.value}]+ba/best'
            opts_list.append({
                'format': fstr,
                'outtmpl': filename_tmplt,
                'recode_video': 'mp4',
                'restrictfilenames': False,
                'writesubtitles': subs_cb.value,
                'subtitleslangs': ['en'],
            })
        if choice in ('mp3','both'):
            opts_list.append({
                'format': 'bestaudio/best',
                'outtmpl': filename_tmplt,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'restrictfilenames': False,
            })

        finished = {'count': 0}

        def progress_hook(d):
            if stop_event.is_set(): raise KeyboardInterrupt
            status = d.get('status')
            fname = os.path.basename(d.get('filename',''))
            if status=='downloading':
                pct   = d.get('_percent_str','0.0%')
                speed = d.get('speed')
                eta   = d.get('eta')
                log_area.value += f"\n⬇️ {fname}: {pct}, ETA: {eta}s"
                if speed: log_area.value += f", Speed: {round(speed/1024,2)} KB/s"
                page.update()
            elif status=='finished':
                finished['count'] += 1
                overall = finished['count'] / len(urls)
                log_area.value += f"\n✅ {fname} finished ({finished['count']}/{len(urls)})"
                progress.value = overall; page.update()
                orig = d.get('filename','')
                dirpath, base = os.path.split(orig)
                name, ext = os.path.splitext(base)
                clean = sanitize_filename(name)+ext
                try: os.rename(orig, os.path.join(dirpath, clean))
                except: pass

        def download_task():
            try:
                for u in urls:
                    if stop_event.is_set(): break
                    for opts in opts_list:
                        for attempt in range(1, RETRY_COUNT+1):
                            try:
                                if stop_event.is_set(): break
                                with yt_dlp.YoutubeDL({**opts, 'progress_hooks':[progress_hook]}) as ydl:
                                    ydl.download([u])
                                break
                            except Exception as err:
                                log_area.value += f"\n⚠️ Attempt {attempt}/{RETRY_COUNT} failed for {u}: {err}"
                                page.update()
                                if attempt==RETRY_COUNT: log_area.value += f"\n❌ Skipping {u} after {RETRY_COUNT} attempts"
            except KeyboardInterrupt:
                log_area.value += '\n🛑 Download stopped.'; page.update()
            except Exception as err:
                log_area.value += f"\n❌ Error: {err}\n{traceback.format_exc()}"; page.update()
            finally:
                download_btn.disabled=False; stop_btn.disabled=True
                if not stop_event.is_set():
                    ft.snack_bar=ft.SnackBar(ft.Text("✅ All downloads complete")); ft.snack_bar.open=True; page.update()
                    if exit_cb.value: page.window_close()
        threading.Thread(target=download_task, daemon=True).start()

    def stop_download(e):
        stop_event.set(); log_area.value+="\n🛑 Cancel requested..."; download_btn.disabled=False; stop_btn.disabled=True; page.update()

    download_btn.on_click=start_download; stop_btn.on_click=stop_download

if __name__=='__main__':
    opts_list = []
    ft.app(target=main)
