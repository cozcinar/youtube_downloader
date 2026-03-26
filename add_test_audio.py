#!/usr/bin/env python3
"""
Quick script to add test1.mp3 and test2.mp3 to GUZELYURT ATIK SU ARITMA TESİSİ.mp4
"""

import os
import subprocess

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    audio_files = ["test1.mp3", "test2.mp3"]
    output_file = "GUZELYURT ATIK SU ARITMA TESİSİ_with_test_audio.mp4"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    missing_audio = []
    for audio_file in audio_files:
        if not os.path.exists(audio_file):
            missing_audio.append(audio_file)

    if missing_audio:
        print(f"Error: Audio files not found: {', '.join(missing_audio)}")
        print("Please make sure test1.mp3 and test2.mp3 are in the current directory.")
        return

    print(f"Replacing audio in {video_file} with:")
    print(f"  - test1.mp3 (Track 1)")
    print(f"  - test2.mp3 (Track 2)")
    print(f"Output: {output_file}")
    print("Note: Original audio will be removed and replaced.")

    # Build ffmpeg command - REPLACE original audio with new ones
    cmd = [
        'ffmpeg',
        '-i', video_file,      # Input video
        '-i', 'test1.mp3',     # Input audio 1
        '-i', 'test2.mp3',     # Input audio 2
        '-map', '0:v',         # Map video from input 0
        # NOTE: NOT mapping original audio (0:a) - we're replacing it
        '-map', '1:a',         # Map audio from input 1 (test1.mp3) as track 0
        '-map', '2:a',         # Map audio from input 2 (test2.mp3) as track 1
        '-c:v', 'copy',        # Copy video without re-encoding
        '-c:a', 'aac',         # Encode audio to AAC
        '-b:a', '128k',        # Set audio bitrate
        '-metadata:s:a:0', 'title=Test Audio 1',  # Title for track 0
        '-metadata:s:a:1', 'title=Test Audio 2',  # Title for track 1
        '-y',                  # Overwrite output file
        output_file
    ]

    print("\nProcessing...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully replaced audio tracks!")
            print(f"Output file: {output_file}")
            print("\nThe video now has 2 audio tracks (original audio removed):")
            print("  Track 0: Test Audio 1 (test1.mp3)")
            print("  Track 1: Test Audio 2 (test2.mp3)")
        else:
            print("❌ Error adding audio tracks:")
            print(f"FFmpeg error: {result.stderr}")

    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

