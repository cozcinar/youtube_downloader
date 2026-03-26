from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
from urllib.error import URLError
import re
import os
import subprocess
import tempfile

video_urls = [
    'https://www.youtube.com/watch?v=RlF4Tf4iqMw'  # Example YouTube URL
]

# Initialize RESOLUTION to None
RESOLUTION = None

def on_progress(stream, chunk, bytes_remaining):
    # Optional: Implement a progress callback if needed
    pass

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL"""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return re.match(youtube_regex, url) is not None

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def merge_video_audio(video_path, audio_path, output_path):
    """Merge video and audio using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error merging video and audio: {e}")
        return False

def download_video(url):
    # Validate URL first
    if not url or not url.strip():
        print("Error: Empty URL provided")
        return

    if not is_valid_youtube_url(url):
        print(f"Error: Invalid YouTube URL: {url}")
        return

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg to merge video and audio streams.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
        return

    try:
        # Create a YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)

        print(f"Title: {yt.title}")
        print(f"Length: {yt.length} seconds")

        # Get the highest quality video stream (video only)
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()

        # Get the highest quality audio stream
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

        if not video_stream:
            print("No video stream found")
            return

        if not audio_stream:
            print("No audio stream found")
            return

        print(f"Video quality: {video_stream.resolution} - {video_stream.fps}fps")
        print(f"Audio quality: {audio_stream.abr}")

        # Create a safe filename
        safe_title = sanitize_filename(yt.title)

        # Create temporary directory for video download only
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download video stream to temp directory
            print("Downloading video stream...")
            video_path = os.path.join(temp_dir, f"{safe_title}_video.mp4")
            video_stream.download(output_path=temp_dir, filename=f"{safe_title}_video.mp4")

            # Download audio stream to current directory (permanent)
            print("Downloading audio stream...")
            audio_filename = f"{safe_title}_audio.mp4"
            audio_path = os.path.join(os.getcwd(), audio_filename)
            audio_stream.download(output_path=os.getcwd(), filename=audio_filename)

            # Merge video and audio
            print("Merging video and audio...")
            output_filename = f"{safe_title}.mp4"
            output_path = os.path.join(os.getcwd(), output_filename)

            if merge_video_audio(video_path, audio_path, output_path):
                print(f"Download completed successfully:")
                print(f"  - Video with audio: {output_filename}")
                print(f"  - Audio only: {audio_filename}")
            else:
                print("Failed to merge video and audio streams")
                print(f"Audio file saved as: {audio_filename}")

    except RegexMatchError as e:
        print(f"Invalid YouTube URL format: {url}")
    except VideoUnavailable as e:
        print(f"Video is unavailable: {e}")
    except URLError as e:
        print(f"Network error occurred: {e}")
    except Exception as e:
        print(f"An error occurred while downloading the video from {url}: {e}")

# Example usage
for url in video_urls:
    download_video(url)
