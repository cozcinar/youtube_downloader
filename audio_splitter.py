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

def get_audio_duration(file_path):
    """Get the duration of an audio file in seconds"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error getting audio duration: {e}")
        return None

def split_audio(input_file, chunk_duration_minutes=4.5):
    """Split audio file into chunks of specified duration"""

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg to split audio files.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
        return False

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return False

    # Get audio duration
    total_duration = get_audio_duration(input_file)
    if total_duration is None:
        print("Error: Could not determine audio duration.")
        return False

    chunk_duration_seconds = chunk_duration_minutes * 60
    total_chunks = int(total_duration / chunk_duration_seconds) + (1 if total_duration % chunk_duration_seconds > 0 else 0)

    print(f"Input file: {input_file}")
    print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Chunk duration: {chunk_duration_minutes} minutes ({chunk_duration_seconds} seconds)")
    print(f"Total chunks to create: {total_chunks}")

    # Create output directory
    input_path = Path(input_file)
    base_name = input_path.stem
    output_dir = input_path.parent / f"{base_name}_chunks"
    output_dir.mkdir(exist_ok=True)

    print(f"Output directory: {output_dir}")
    print("\nSplitting audio...")

    # Split the audio file
    for i in range(total_chunks):
        start_time = i * chunk_duration_seconds
        output_file = output_dir / f"{base_name}_chunk_{i+1:03d}.mp4"

        # Calculate remaining time for the last chunk
        remaining_time = total_duration - start_time
        current_chunk_duration = min(chunk_duration_seconds, remaining_time)

        print(f"Creating chunk {i+1}/{total_chunks}: {output_file.name}")

        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(current_chunk_duration),
            '-vn',  # Disable video processing (audio only)
            '-acodec', 'copy',  # Copy audio codec without re-encoding
            '-avoid_negative_ts', 'make_zero',
            '-y',  # Overwrite output files
            str(output_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            # If copy fails, try re-encoding with AAC
            print(f"Copy method failed for chunk {i+1}, trying re-encoding...")

            cmd_reencode = [
                'ffmpeg', '-i', input_file,
                '-ss', str(start_time),
                '-t', str(current_chunk_duration),
                '-vn',  # Disable video processing (audio only)
                '-acodec', 'aac',  # Re-encode to AAC
                '-b:a', '128k',  # Set audio bitrate
                '-avoid_negative_ts', 'make_zero',
                '-y',  # Overwrite output files
                str(output_file)
            ]

            try:
                subprocess.run(cmd_reencode, capture_output=True, check=True)
                print(f"Successfully re-encoded chunk {i+1}")
            except subprocess.CalledProcessError as e2:
                print(f"Error creating chunk {i+1} (both copy and re-encode failed): {e2}")
                # Print stderr for debugging
                if e2.stderr:
                    print(f"FFmpeg error: {e2.stderr.decode()}")
                return False

    print(f"\nSplitting completed successfully!")
    print(f"Created {total_chunks} chunks in: {output_dir}")
    return True

def main():
    """Main function to handle command line arguments or interactive input"""

    # Check if file path is provided as command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Interactive mode - list available MP4 files in current directory
        mp4_files = [f for f in os.listdir('.') if f.lower().endswith('.mp4')]

        if not mp4_files:
            print("No MP4 files found in the current directory.")
            input_file = input("Please enter the path to your MP4 audio file: ").strip()
        else:
            print("Available MP4 files in current directory:")
            for i, file in enumerate(mp4_files, 1):
                print(f"{i}. {file}")

            while True:
                try:
                    choice = input(f"\nSelect a file (1-{len(mp4_files)}) or enter custom path: ").strip()

                    # Check if it's a number (file selection)
                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(mp4_files):
                            input_file = mp4_files[choice_num - 1]
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(mp4_files)}")
                    else:
                        # Treat as custom file path
                        input_file = choice
                        break
                except ValueError:
                    print("Invalid input. Please try again.")

    # Ask for chunk duration (optional)
    chunk_duration = 4.5  # default
    duration_input = input(f"Enter chunk duration in minutes (default: {chunk_duration}): ").strip()
    if duration_input:
        try:
            chunk_duration = float(duration_input)
            if chunk_duration <= 0:
                print("Duration must be positive. Using default 4.5 minutes.")
                chunk_duration = 4.5
        except ValueError:
            print("Invalid duration. Using default 4.5 minutes.")

    # Split the audio file
    success = split_audio(input_file, chunk_duration)

    if success:
        print("\n✅ Audio splitting completed successfully!")
    else:
        print("\n❌ Audio splitting failed.")

if __name__ == "__main__":
    main()
