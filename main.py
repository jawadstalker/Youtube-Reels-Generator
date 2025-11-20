import os
import re
from urllib.parse import urlparse, parse_qs
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip

def download_youtube_video(url, start_time, output_path="downloads"):
    """
    Download YouTube video and cut specific segment
    """
    try:
        # Create downloads folder if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[height<=480]',  # Max 720p to avoid huge files
            'outtmpl': os.path.join(output_path, 'temp_video.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }

        print("📹 Getting video information...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            
            print(f"📹 Downloading: {video_title}")
            
            # Download the video
            ydl.download([url])
            
            # Find the downloaded file
            temp_files = [f for f in os.listdir(output_path) if f.startswith('temp_video.')]
            if not temp_files:
                print("❌ Downloaded file not found!")
                return None
                
            video_path = os.path.join(output_path, temp_files[0])

        # Cut the video
        safe_title = re.sub(r'[^\w\-_.]', '', video_title.replace(' ', '_'))
        output_filename = f"cut_{safe_title}.mp4"
        output_filepath = os.path.join(output_path, output_filename)
        
        cut_video(video_path, output_filepath, start_time, start_time + 30)
        
        # Clean up temporary file
        os.remove(video_path)
        
        print(f"✅ Download and cutting completed: {output_filename}")
        return output_filepath
        
    except Exception as e:
        print(f"❌ Error processing video: {str(e)}")
        return None

def cut_video(input_path, output_path, start_time, end_time):
    """
    Cut video from start time to end time
    """
    try:
        # Load video
        video = VideoFileClip(input_path)
        
        # Validate time range
        if start_time > video.duration:
            raise ValueError(f"Start time {start_time}s exceeds video duration {video.duration}s")
        
        end_time = min(end_time, video.duration)
        
        # Cut video
        cut_video = video.subclip(start_time, end_time)
        
        # Save cut video
        cut_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Close videos to free resources
        video.close()
        cut_video.close()
        
        print(f"✂️ Video cut from {start_time}s to {end_time}s")
        
    except Exception as e:
        print(f"❌ Error cutting video: {str(e)}")
        raise

def get_time_input(prompt):
    """
    Get time input from user in minutes:seconds format
    """
    while True:
        try:
            time_str = input(prompt)
            if ':' in time_str:
                minutes, seconds = map(int, time_str.split(':'))
                total_seconds = minutes * 60 + seconds
            else:
                total_seconds = int(time_str)
            
            if total_seconds >= 0:
                return total_seconds
            else:
                print("❌ Time must be a positive number!")
        except ValueError:
            print("❌ Invalid time format! Please use minutes:seconds or seconds")

def main():
    """
    Main function
    """
    print("🎬 YouTube 30-Second Clip Downloader")
    print("=" * 50)
    
    # Get user input
    youtube_url = input("🔗 Enter YouTube URL: ").strip()
    
    print("\n⏰ Enter start time:")
    print("Example: 120 or 2:00 (for 2 minutes)")
    start_time = get_time_input("Start time: ")
    
    # Download and cut video
    result = download_youtube_video(youtube_url, start_time)
    
    if result:
        print(f"\n🎉 Operation completed successfully!")
        print(f"📁 File saved at: {result}")
    else:
        print("\n❌ Operation failed!")

if __name__ == "__main__":
    main()