import subprocess
from pytube import YouTube
import openai
import os

# ست کردن کلید OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"

def download_video_and_subs(url):
    yt = YouTube(url)
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video_path = "video.mp4"
    video_stream.download(filename=video_path)

    if 'en' in yt.captions:
        caption = yt.captions['en']
    elif 'en-US' in yt.captions:
        caption = yt.captions['en-US']
    else:
        caption = None

    if caption:
        subs_text = caption.generate_srt_captions()
        with open("subtitle.srt", "w", encoding="utf-8") as f:
            f.write(subs_text)
        print("✅ Subtitle downloaded.")
    else:
        subs_text = ""
        print("⚠️ No English subtitles found.")

    return video_path, subs_text

def get_best_30_seconds(subs_text):
    if not subs_text:
        return 0, 30  

    prompt = f"""
    You are a video editor AI. Given the following transcript of a YouTube video, select the most engaging 30 seconds
    for a short reel. Provide start and end times in seconds as JSON: {{"start": , "end": }}.
    Transcript:
    {subs_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}]
    )

    import json
    try:
        times_json = response['choices'][0]['message']['content']
        times = json.loads(times_json)
        return times["start"], times["end"]
    except:
        return 0, 30

def cut_clip(video_path, start, end, output_path="reel.mp4"):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path
    ])
    return output_path

def add_subtitles(video_path, subs_path, output_path="reel_with_subs.mp4"):
    if not os.path.exists(subs_path):
        return video_path  
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={subs_path}",
        output_path
    ])
    return output_path

if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    video_path, subs_text = download_video_and_subs(url)
    start, end = get_best_30_seconds(subs_text)
    clip_path = cut_clip(video_path, start, end)
    final_path = add_subtitles(clip_path, "subtitle.srt")
    print(f"✅ Finished! Output: {final_path}")
