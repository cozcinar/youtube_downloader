#!/usr/bin/env python3
"""
Script to add subtitle file to video and set it as default
"""

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

def add_subtitles_to_video(video_file, subtitle_file, output_file=None, subtitle_language="en", subtitle_title="English"):
    """Add subtitle file to video as default track"""

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return False

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return False

    # Generate output filename if not provided
    if output_file is None:
        video_path = Path(video_file)
        output_file = video_path.parent / f"{video_path.stem}_with_subtitles{video_path.suffix}"

    print(f"Input video: {video_file}")
    print(f"Subtitle file: {subtitle_file}")
    print(f"Output file: {output_file}")
    print(f"Subtitle language: {subtitle_language}")
    print(f"Subtitle title: {subtitle_title}")

    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_file,           # Input video
        '-i', subtitle_file,        # Input subtitle file
        '-map', '0:v',              # Map video from input 0
        '-map', '0:a',              # Map audio from input 0
        '-map', '1:s',              # Map subtitle from input 1
        '-c:v', 'copy',             # Copy video without re-encoding
        '-c:a', 'copy',             # Copy audio without re-encoding
        '-c:s', 'mov_text',         # Use mov_text codec for MP4 subtitles
        '-metadata:s:s:0', f'language={subtitle_language}',     # Set subtitle language
        '-metadata:s:s:0', f'title={subtitle_title}',           # Set subtitle title
        '-disposition:s:0', 'default',                          # Set as default subtitle
        '-y',                       # Overwrite output file
        str(output_file)
    ]

    print("\nProcessing...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully added subtitles to video!")
            print(f"Output file: {output_file}")
            print("\nThe video now has embedded subtitles that will display by default.")
            print("You can toggle subtitles on/off in your media player.")
            return True
        else:
            print("❌ Error adding subtitles:")
            print(f"FFmpeg error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_mode():
    """Interactive mode for selecting files"""
    print("Add Subtitles to Video")
    print("=====================")
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

    # Select subtitle file
    subtitle_extensions = ('.vtt', '.srt', '.ass', '.ssa', '.sub')
    available_subtitles = [f for f in os.listdir('.') if f.lower().endswith(subtitle_extensions)]

    if available_subtitles:
        print(f"\nAvailable subtitle files:")
        for i, file in enumerate(available_subtitles, 1):
            print(f"{i}. {file}")
        print()

        while True:
            try:
                choice = input(f"Select subtitle file (1-{len(available_subtitles)}) or enter custom path: ").strip()

                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(available_subtitles):
                        subtitle_file = available_subtitles[choice_num - 1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(available_subtitles)}")
                else:
                    if os.path.exists(choice):
                        subtitle_file = choice
                        break
                    else:
                        print(f"File not found: {choice}")
            except ValueError:
                print("Invalid input. Please try again.")
    else:
        subtitle_file = input("Enter path to subtitle file: ").strip()
        if not os.path.exists(subtitle_file):
            print(f"Subtitle file not found: {subtitle_file}")
            return

    # Ask for subtitle language and title
    language = input("Enter subtitle language code (default: en): ").strip() or "en"
    title = input("Enter subtitle title (default: English): ").strip() or "English"

    # Ask for output filename
    default_output = Path(video_file).stem + "_with_subtitles" + Path(video_file).suffix
    output_file = input(f"Output filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output

    # Process the files
    add_subtitles_to_video(video_file, subtitle_file, output_file, language, title)

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
        # Command line mode: script.py video_file subtitle_file [output_file] [language] [title]
        video_file = sys.argv[1]
        subtitle_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        language = sys.argv[4] if len(sys.argv) > 4 else "en"
        title = sys.argv[5] if len(sys.argv) > 5 else "English"

        add_subtitles_to_video(video_file, subtitle_file, output_file, language, title)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
