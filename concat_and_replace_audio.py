#!/usr/bin/env python3
"""
Script to concatenate test1.mp3 and test2.mp3 into a single audio track
and replace the original audio in GUZELYURT ATIK SU ARITMA TESİSİ.mp4
"""

import os
import subprocess
import tempfile

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    audio_files = ["test1.mp3", "test2.mp3"]
    output_file = "GUZELYURT ATIK SU ARITMA TESİSİ_with_concatenated_audio.mp4"

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

    print(f"Concatenating audio files:")
    print(f"  1. test1.mp3")
    print(f"  2. test2.mp3 (will play after test1.mp3)")
    print(f"Replacing audio in: {video_file}")
    print(f"Output: {output_file}")

    # Create a temporary file list for ffmpeg concat
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        concat_file = f.name
        f.write(f"file '{os.path.abspath('test1.mp3')}'\n")
        f.write(f"file '{os.path.abspath('test2.mp3')}'\n")

    try:
        print("\nStep 1: Concatenating audio files...")

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
            return

        print("✅ Audio files concatenated successfully")

        print("\nStep 2: Replacing video audio...")

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
            output_file
        ]

        result = subprocess.run(replace_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully replaced video audio!")
            print(f"Output file: {output_file}")
            print("\nThe video now has a single audio track:")
            print("  - test1.mp3 followed by test2.mp3 (concatenated)")
        else:
            print("❌ Error replacing video audio:")
            print(f"FFmpeg error: {result.stderr}")

    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up temporary files
        try:
            os.unlink(concat_file)
            if 'temp_audio_path' in locals():
                os.unlink(temp_audio_path)
        except:
            pass

if __name__ == "__main__":
    main()
