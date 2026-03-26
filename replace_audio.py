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

def replace_audio_tracks(video_file, audio_files, output_file=None):
    """Replace original audio with new audio tracks"""

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
        output_file = video_path.parent / f"{video_path.stem}_new_audio{video_path.suffix}"

    print(f"Input video: {video_file}")
    print(f"Replacing original audio with:")
    for i, audio_file in enumerate(audio_files, 1):
        print(f"  Track {i}: {audio_file}")
    print(f"Output file: {output_file}")
    print("Note: Original audio will be completely removed.")

    # Build ffmpeg command
    cmd = ['ffmpeg']

    # Add input video
    cmd.extend(['-i', video_file])

    # Add input audio files
    for audio_file in audio_files:
        cmd.extend(['-i', audio_file])

    # Map video stream from first input (no original audio)
    cmd.extend(['-map', '0:v'])

    # Map all new audio streams (skip original audio completely)
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
        cmd.extend([f'-metadata:s:a:{i}', f'title={audio_name}'])
        cmd.extend([f'-metadata:s:a:{i}', f'language=und'])

    # Overwrite output file
    cmd.extend(['-y'])

    # Add output file
    cmd.append(str(output_file))

    print(f"\nProcessing...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully replaced audio tracks!")
            print(f"Output file: {output_file}")
            print(f"\nThe video now has {len(audio_files)} audio track(s):")
            for i, audio_file in enumerate(audio_files):
                print(f"  Track {i}: {Path(audio_file).stem}")
            return True
        else:
            print(f"❌ Error replacing audio tracks:")
            print(f"FFmpeg error: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ffmpeg: {e}")
        return False

def interactive_mode():
    """Interactive mode for selecting files"""
    print("Replace Video Audio")
    print("==================")
    print()

    # Select video file
    video_files = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]

    if video_files:
        print("Available video files:")
        for i, file in enumerate(video_files, 1):
            print(f"{i}. {file}")
        print()

        while True:
            try:
                choice = input(f"Select video file (1-{len(video_files)}) or enter custom path: ").strip()

                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(video_files):
                        video_file = video_files[choice_num - 1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(video_files)}")
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

        print("Select audio files to replace with (enter numbers separated by spaces):")
        selection = input("Selection: ").strip()

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
    default_output = Path(video_file).stem + "_new_audio" + Path(video_file).suffix
    output_file = input(f"Output filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output

    # Process the files
    replace_audio_tracks(video_file, audio_files, output_file)

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

        replace_audio_tracks(video_file, audio_files)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
