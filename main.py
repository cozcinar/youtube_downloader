from pytubefix import YouTube
from pytubefix.cli import on_progress

video_urls = [
    ''
]

# Initialize RESOLUTION to None
RESOLUTION = None

def on_progress(stream, chunk, bytes_remaining):
    # Optional: Implement a progress callback if needed
    pass

def find_highest_resolution(yt):
    resolutions = []
    for stream in yt.streams.filter(type="video"):
        if stream.resolution:
            resolutions.append(stream.resolution)
    return max(resolutions, key=lambda res: int(res[:-1]))

def download_video(url):
    global RESOLUTION
    try:
        # Create a YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)

        # Find the highest resolution available
        RESOLUTION = find_highest_resolution(yt)
        print(f"Highest resolution found: {RESOLUTION}")

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
            print("Download completed successfully.")
        else:
            print(f"No stream found with resolution {RESOLUTION}")

    except URLError as e:
        print(f"Network error occurred: {e}")
    except Exception as e:
        print(f"An error occurred while downloading the video from {url}: {e}")

# Example usage
for url in video_urls:
    download_video(url)