from pytubefix import YouTube
from pytubefix.cli import on_progress

# List of video URLs to download
video_urls = [
    'https://www.youtube.com/watch?v=x3pCAXQHpc0',
    'https://www.youtube.com/watch?v=DwmfUFHu4m8',
    'https://www.youtube.com/watch?v=p3X8AU6eFnM',
    'https://www.youtube.com/watch?v=8JHVEXxFxOE',
    'https://www.youtube.com/watch?v=XBo7tUJVVXU',
    'https://www.youtube.com/watch?v=FR0TPPOjSRk',
    'https://www.youtube.com/watch?v=xnYsv1diMH0',
    'https://www.youtube.com/watch?v=mdqy9kmUeeI',
    'https://www.youtube.com/watch?v=0PGlz9h8c_8',
    'https://www.youtube.com/watch?v=Z1AIHCfuOT0'
]

# Desired resolution for the video download
RESOLUTION = '1080p'

def download_video(url):
    try:
        # Create a YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)

        # Find the stream with the desired resolution
        video_stream = None
        for stream in yt.streams:
            if stream.resolution == RESOLUTION:
                video_stream = stream
                break

        # If the stream is found, download it
        if video_stream:
            print(f"Downloading: {yt.title} in {video_stream.resolution}")
            video_stream.download()
            print("Download completed.\n")
        else:
            print(f"No stream found for resolution {RESOLUTION} for video: {yt.title}\n")

    except Exception as e:
        print(f"An error occurred while downloading the video from {url}: {e}\n")

if __name__ == "__main__":
    # Iterate over each URL in the list and download the video
    for video_url in video_urls:
        download_video(video_url)
