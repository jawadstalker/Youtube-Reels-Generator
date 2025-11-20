import subprocess
import yt_dlp
import os

# ------------------------------------------
# Download subtitles only (no full video)
# ------------------------------------------
def download_subtitles_only(url, subs_name="subtitle.srt"):
    ydl_opts = {
        "skip_download": True,          # فقط زیرنویس
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "outtmpl": "temp",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # پیدا کردن فایل .vtt
    vtt_file = None
    for f in os.listdir():
        if f.endswith(".vtt"):
            vtt_file = f
            break

    if vtt_file:
        # تبدیل به srt
        subprocess.run(["ffmpeg", "-y", "-i", vtt_file, subs_name])
        with open(subs_name, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("⚠️ No English subtitles found.")
        return ""


# ------------------------------------------
# Download selected 30-second clip
# ------------------------------------------
def download_selected_clip(url, start, end, output="reel.mp4"):
    duration = end - start

    ydl_opts = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # پیدا کردن بهترین فرمت mp4
    formats = info.get("formats", [])
    best_format = None
    for f in formats:
        if f.get("ext") == "mp4" and f.get("height") and f["height"] <= 720:
            best_format = f
            break

    if not best_format:
        raise Exception("No suitable MP4 format found")

    video_url = best_format["url"]

    # برش با ffmpeg
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", video_url,
        "-t", str(duration),
        "-c", "copy",
        output
    ])
    return output



# ------------------------------------------
# Burn subtitles on the clip
# ------------------------------------------
def add_subtitles(video_path, subs_path, output="reel_with_subs.mp4"):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={subs_path}",
        output
    ])
    return output


# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    url = input("Enter YouTube URL: ")

    # دانلود زیرنویس
    subs_text = download_subtitles_only(url)

    # کاربر دستی زمان شروع و پایان را وارد می‌کند
    start = float(input("Enter start time in seconds: "))
    end = float(input("Enter end time in seconds: "))

    print("🎬 Selected section:", start, "→", end)

    # دانلود و برش ویدیو
    clip = download_selected_clip(url, start, end)

    # چسباندن زیرنویس
    final = add_subtitles(clip, "subtitle.srt")

    print("✅ Done! Output:", final)
