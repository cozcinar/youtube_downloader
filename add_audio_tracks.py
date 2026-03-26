import os
import subprocess
import sys
from pathlib import Path

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_media_info(file_path):
    """Get basic information about a media file"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def add_audio_tracks(video_file, audio_files, output_file=None):
    """Add multiple audio tracks to a video file"""

    # Check if video file exists
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return False

    # Check if all audio files exist
    for audio_file in audio_files:
        if not os.path.exists(audio_file):
            print(f"Error: Audio file '{audio_file}' not found.")
            return False

    # Generate output filename if not provided
    if output_file is None:
        video_path = Path(video_file)
        output_file = video_path.parent / f"{video_path.stem}_with_audio_tracks{video_path.suffix}"

    print(f"Input video: {video_file}")
    print(f"Audio tracks to add:")
    for i, audio_file in enumerate(audio_files, 1):
        print(f"  Track {i}: {audio_file}")
    print(f"Output file: {output_file}")

    # Build ffmpeg command
    cmd = ['ffmpeg']

    # Add input video
    cmd.extend(['-i', video_file])

    # Add input audio files
    for audio_file in audio_files:
        cmd.extend(['-i', audio_file])

    # Map video stream from first input
    cmd.extend(['-map', '0:v'])

    # Map original audio stream from video (if exists)
    cmd.extend(['-map', '0:a?'])

    # Map all additional audio streams
    for i in range(len(audio_files)):
        cmd.extend(['-map', f'{i+1}:a'])

    # Video codec - copy without re-encoding
    cmd.extend(['-c:v', 'copy'])

    # Audio codec - encode to AAC for compatibility
    cmd.extend(['-c:a', 'aac'])
    cmd.extend(['-b:a', '128k'])

    # Add metadata for audio tracks
    for i, audio_file in enumerate(audio_files):
        audio_name = Path(audio_file).stem
        track_index = i + 1  # +1 because track 0 is original audio (if exists)
        if os.path.exists(video_file) and get_media_info(video_file) and '"codec_type": "audio"' in get_media_info(video_file):
            track_index = i + 2  # +2 if original video has audio
        else:
            track_index = i + 1  # +1 if original video has no audio

        cmd.extend([f'-metadata:s:a:{track_index}', f'title={audio_name}'])
        cmd.extend([f'-metadata:s:a:{track_index}', f'language=und'])

    # Overwrite output file
    cmd.extend(['-y'])

    # Add output file
    cmd.append(str(output_file))

    print(f"\nProcessing...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully added audio tracks!")
            print(f"Output file: {output_file}")
            return True
        else:
            print(f"❌ Error adding audio tracks:")
            print(f"FFmpeg error: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ffmpeg: {e}")
        return False

def interactive_mode():
    """Interactive mode for selecting files"""
    print("Add Audio Tracks to Video")
    print("========================")
    print()

    # Select video file
    mp4_files = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]

    if mp4_files:
        print("Available video files:")
        for i, file in enumerate(mp4_files, 1):
            print(f"{i}. {file}")
        print()

        while True:
            try:
                choice = input(f"Select video file (1-{len(mp4_files)}) or enter custom path: ").strip()

                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(mp4_files):
                        video_file = mp4_files[choice_num - 1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(mp4_files)}")
                else:
                    if os.path.exists(choice):
                        video_file = choice
                        break
                    else:
                        print(f"File not found: {choice}")
            except ValueError:
                print("Invalid input. Please try again.")
    else:
        video_file = input("Enter path to video file: ").strip()
        if not os.path.exists(video_file):
            print(f"Video file not found: {video_file}")
            return

    # Select audio files
    audio_files = []
    audio_extensions = ('.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg')
    available_audio = [f for f in os.listdir('.') if f.lower().endswith(audio_extensions)]

    if available_audio:
        print(f"\nAvailable audio files:")
        for i, file in enumerate(available_audio, 1):
            print(f"{i}. {file}")
        print()

        print("Select audio files to add (enter numbers separated by spaces, or 'all' for all files):")
        selection = input("Selection: ").strip()

        if selection.lower() == 'all':
            audio_files = available_audio
        else:
            try:
                indices = [int(x) for x in selection.split()]
                for idx in indices:
                    if 1 <= idx <= len(available_audio):
                        audio_files.append(available_audio[idx - 1])
                    else:
                        print(f"Warning: Index {idx} is out of range, skipping...")
            except ValueError:
                print("Invalid selection format. Please enter numbers separated by spaces.")
                return
    else:
        print("\nNo audio files found in current directory.")
        while True:
            audio_file = input("Enter path to audio file (or 'done' to finish): ").strip()
            if audio_file.lower() == 'done':
                break
            if os.path.exists(audio_file):
                audio_files.append(audio_file)
            else:
                print(f"Audio file not found: {audio_file}")

    if not audio_files:
        print("No audio files selected.")
        return

    # Ask for output filename
    default_output = Path(video_file).stem + "_with_audio_tracks" + Path(video_file).suffix
    output_file = input(f"Output filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output

    # Process the files
    add_audio_tracks(video_file, audio_files, output_file)

def main():
    """Main function"""

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
        return

    if len(sys.argv) >= 3:
        # Command line mode: script.py video_file audio1 audio2 ...
        video_file = sys.argv[1]
        audio_files = sys.argv[2:]

        add_audio_tracks(video_file, audio_files)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()

