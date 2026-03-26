import os
import subprocess
import sys
import tempfile
from pathlib import Path

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def concatenate_and_replace_audio(video_file, audio_files, output_file=None):
    """Concatenate multiple audio files and replace video audio"""

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
        output_file = video_path.parent / f"{video_path.stem}_concatenated_audio{video_path.suffix}"

    print(f"Input video: {video_file}")
    print(f"Concatenating audio files in order:")
    for i, audio_file in enumerate(audio_files, 1):
        print(f"  {i}. {audio_file}")
    print(f"Output file: {output_file}")
    print("Note: Audio files will play sequentially, original video audio will be replaced.")

    # Create a temporary file list for ffmpeg concat
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        concat_file = f.name
        for audio_file in audio_files:
            f.write(f"file '{os.path.abspath(audio_file)}'\n")

    try:
        print(f"\nStep 1: Concatenating {len(audio_files)} audio files...")

        # First, concatenate the audio files
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_audio_path = temp_audio.name

        concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            temp_audio_path
        ]

        result = subprocess.run(concat_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error concatenating audio files:")
            print(f"FFmpeg error: {result.stderr}")
            return False

        print("✅ Audio files concatenated successfully")

        print("\nStep 2: Replacing video audio with concatenated audio...")

        # Now replace the video audio with the concatenated audio
        replace_cmd = [
            'ffmpeg',
            '-i', video_file,           # Input video
            '-i', temp_audio_path,      # Input concatenated audio
            '-map', '0:v',              # Map video from input 0
            '-map', '1:a',              # Map audio from input 1 (concatenated)
            '-c:v', 'copy',             # Copy video without re-encoding
            '-c:a', 'aac',              # Encode audio to AAC
            '-b:a', '128k',             # Set audio bitrate
            '-shortest',                # Match the shortest stream duration
            '-y',                       # Overwrite output file
            str(output_file)
        ]

        result = subprocess.run(replace_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully replaced video audio with concatenated audio!")
            print(f"Output file: {output_file}")
            print(f"\nThe video now has a single audio track containing all {len(audio_files)} audio files played sequentially.")
            return True
        else:
            print("❌ Error replacing video audio:")
            print(f"FFmpeg error: {result.stderr}")
            return False

    finally:
        # Clean up temporary files
        try:
            os.unlink(concat_file)
            if 'temp_audio_path' in locals():
                os.unlink(temp_audio_path)
        except:
            pass

def interactive_mode():
    """Interactive mode for selecting files"""
    print("Concatenate Audio Files and Replace Video Audio")
    print("==============================================")
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

    # Select audio files in order
    audio_files = []
    audio_extensions = ('.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg')
    available_audio = [f for f in os.listdir('.') if f.lower().endswith(audio_extensions)]

    if available_audio:
        print(f"\nAvailable audio files:")
        for i, file in enumerate(available_audio, 1):
            print(f"{i}. {file}")
        print()

        print("Select audio files in the order you want them concatenated:")
        print("(Enter numbers separated by spaces, e.g., '1 3 2' to play file 1, then 3, then 2)")
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
        print("Enter audio file paths in the order you want them concatenated:")
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

    if len(audio_files) < 2:
        print("You need at least 2 audio files to concatenate.")
        return

    # Ask for output filename
    default_output = Path(video_file).stem + "_concatenated_audio" + Path(video_file).suffix
    output_file = input(f"Output filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output

    # Process the files
    concatenate_and_replace_audio(video_file, audio_files, output_file)

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

        concatenate_and_replace_audio(video_file, audio_files)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
