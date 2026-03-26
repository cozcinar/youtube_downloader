#!/usr/bin/env python3
"""
Quick script to add translate.vtt subtitles to GUZELYURT ATIK SU ARITMA TESİSİ.mp4
"""

import os
import subprocess

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    subtitle_file = "translate.vtt"
    output_file = "GUZELYURT ATIK SU ARITMA TESİSİ_with_subtitles.mp4"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return

    print(f"Adding subtitles to: {video_file}")
    print(f"Subtitle file: {subtitle_file}")
    print(f"Output: {output_file}")
    print("Note: Subtitles will be embedded and set as default.")

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
        '-metadata:s:s:0', 'language=en',           # Set subtitle language
        '-metadata:s:s:0', 'title=English Translation',  # Set subtitle title
        '-disposition:s:0', 'default',              # Set as default subtitle
        '-y',                       # Overwrite output file
        output_file
    ]

    print("\nProcessing...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully added subtitles to video!")
            print(f"Output file: {output_file}")
            print("\nThe video now has embedded English subtitles that will display by default.")
            print("You can toggle subtitles on/off in your media player.")
        else:
            print("❌ Error adding subtitles:")
            print(f"FFmpeg error: {result.stderr}")

    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
