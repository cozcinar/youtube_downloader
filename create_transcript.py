import sys
import os
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
from urllib.error import URLError


def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_caption_tracks(yt):
    try:
        renderer = yt.vid_info.get('captions', {}).get('playerCaptionsTracklistRenderer', {})
        return renderer.get('captionTracks', [])
    except Exception:
        return []


def pick_best_caption(tracks):
    manual = [t for t in tracks if 'kind' not in t]
    auto = [t for t in tracks if t.get('kind') == 'asr']

    for group in [manual, auto]:
        en = [t for t in group if t['languageCode'].startswith('en')]
        if en:
            return en[0]
        if group:
            return group[0]
    return None


def transcript_from_captions(yt):
    tracks = get_caption_tracks(yt)
    if not tracks:
        return None

    track = pick_best_caption(tracks)
    if not track:
        return None

    kind = "auto-generated" if track.get('kind') == 'asr' else "manual"
    print(f"Found {kind} captions ({track['languageCode']})")

    data = urllib.request.urlopen(track['baseUrl']).read().decode('utf-8')
    root = ET.fromstring(data)
    lines = []
    for p in root.iter('p'):
        text = ''.join(p.itertext()).strip()
        if text:
            lines.append(unescape(text))
    return '\n'.join(lines)


def transcript_from_whisper(yt):
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is required for audio transcription.")
        print("On macOS: brew install ffmpeg")
        return None

    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
    if not audio_stream:
        print("Error: No audio stream found")
        return None

    from faster_whisper import WhisperModel

    print(f"Downloading audio ({audio_stream.abr})...")
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "audio.mp4")
        audio_stream.download(output_path=temp_dir, filename="audio.mp4")

        print("Loading Faster-Whisper model (base). First run will download ~150MB...")
        model = WhisperModel("base", compute_type="int8")

        print("Transcribing...")
        segments, info = model.transcribe(audio_path)
        print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")

        return '\n'.join(seg.text.strip() for seg in segments)


def create_transcript(url):
    try:
        yt = YouTube(url)
    except RegexMatchError:
        print(f"Error: Invalid YouTube URL: {url}")
        return False
    except VideoUnavailable as e:
        print(f"Error: Video unavailable: {e}")
        return False
    except URLError as e:
        print(f"Error: Network error: {e}")
        return False

    print(f"Title: {yt.title}")
    print(f"Length: {yt.length} seconds")

    text = transcript_from_captions(yt)
    if text is None:
        print("No captions available. Falling back to Faster-Whisper...")
        text = transcript_from_whisper(yt)

    if text is None:
        print("Error: Could not generate transcript")
        return False

    safe_title = sanitize_filename(yt.title)
    output_path = os.path.join(os.getcwd(), f"{safe_title}_transcript.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Transcript saved: {output_path}")
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <youtube-url>")
        sys.exit(1)

    sys.exit(0 if create_transcript(sys.argv[1]) else 1)
