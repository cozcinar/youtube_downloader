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

def clean_audio_file(input_file, output_file=None):
    """Clean audio file by removing any video streams and re-encoding if necessary"""

    if output_file is None:
        # Create output filename with _clean suffix
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"

    print(f"Cleaning: {input_file}")
    print(f"Output: {output_file}")

    # First try: Extract audio only without re-encoding
    cmd_copy = [
        'ffmpeg', '-i', str(input_file),
        '-vn',  # No video
        '-acodec', 'copy',  # Copy audio without re-encoding
        '-y',  # Overwrite output files
        str(output_file)
    ]

    try:
        subprocess.run(cmd_copy, capture_output=True, check=True)
        print("✅ Successfully cleaned (audio copied)")
        return True
    except subprocess.CalledProcessError:
        print("Copy method failed, trying re-encoding...")

        # Second try: Re-encode to AAC
        cmd_reencode = [
            'ffmpeg', '-i', str(input_file),
            '-vn',  # No video
            '-acodec', 'aac',  # Re-encode to AAC
            '-b:a', '128k',  # Set audio bitrate
            '-ar', '44100',  # Set sample rate
            '-ac', '2',  # Set to stereo
            '-y',  # Overwrite output files
            str(output_file)
        ]

        try:
            subprocess.run(cmd_reencode, capture_output=True, check=True)
            print("✅ Successfully cleaned (audio re-encoded)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clean audio file: {e}")
            if e.stderr:
                print(f"FFmpeg error: {e.stderr.decode()}")
            return False

def clean_directory(directory_path):
    """Clean all MP4 files in a directory"""
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Directory not found: {directory_path}")
        return False

    mp4_files = list(directory.glob("*.mp4"))

    if not mp4_files:
        print(f"No MP4 files found in: {directory_path}")
        return False

    print(f"Found {len(mp4_files)} MP4 files to clean")

    success_count = 0
    for mp4_file in mp4_files:
        # Skip files that are already cleaned
        if "_clean" in mp4_file.stem:
            print(f"Skipping already cleaned file: {mp4_file.name}")
            continue

        if clean_audio_file(mp4_file):
            success_count += 1

    print(f"\n✅ Successfully cleaned {success_count}/{len(mp4_files)} files")
    return success_count > 0

def main():
    """Main function"""

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
        return

    if len(sys.argv) > 1:
        input_path = sys.argv[1]

        if os.path.isfile(input_path):
            # Single file
            clean_audio_file(input_path)
        elif os.path.isdir(input_path):
            # Directory
            clean_directory(input_path)
        else:
            print(f"Path not found: {input_path}")
    else:
        # Interactive mode
        print("Audio Chunk Cleaner")
        print("==================")
        print()

        # Look for chunk directories in current directory
        chunk_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and '_chunks' in d]

        if chunk_dirs:
            print("Found chunk directories:")
            for i, dir_name in enumerate(chunk_dirs, 1):
                print(f"{i}. {dir_name}")
            print()

            while True:
                try:
                    choice = input(f"Select directory (1-{len(chunk_dirs)}) or enter custom path: ").strip()

                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(chunk_dirs):
                            selected_dir = chunk_dirs[choice_num - 1]
                            clean_directory(selected_dir)
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(chunk_dirs)}")
                    else:
                        # Custom path
                        if os.path.exists(choice):
                            if os.path.isdir(choice):
                                clean_directory(choice)
                            else:
                                clean_audio_file(choice)
                            break
                        else:
                            print(f"Path not found: {choice}")
                except ValueError:
                    print("Invalid input. Please try again.")
        else:
            # No chunk directories found, ask for path
            path = input("Enter path to MP4 file or directory: ").strip()

            if os.path.isfile(path):
                clean_audio_file(path)
            elif os.path.isdir(path):
                clean_directory(path)
            else:
                print(f"Path not found: {path}")

if __name__ == "__main__":
    main()

