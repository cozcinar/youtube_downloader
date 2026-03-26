#!/usr/bin/env python3
"""
Quick script to burn translate.vtt subtitles directly into video frames
"""

import os
import subprocess

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    subtitle_file = "translate.vtt"
    output_file = "GUZELYURT ATIK SU ARITMA TESİSİ_burned_subtitles.mp4"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return

    print(f"🔥 Burning subtitles into video frames...")
    print(f"📹 Video: {video_file}")
    print(f"📝 Subtitles: {subtitle_file}")
    print(f"💾 Output: {output_file}")
    print()
    print("⏳ This process may take several minutes...")
    print("The subtitles will be permanently burned into the video image.")
    print()

    # Build ffmpeg command with optimized subtitle burning
    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-vf', (
            f"subtitles={subtitle_file}:"
            "force_style='"
            "Fontname=Arial Bold,"
            "Fontsize=20,"
            "PrimaryColour=&HFFFFFF,"    # White text
            "OutlineColour=&H000000,"    # Black outline
            "BackColour=&H80000000,"     # Semi-transparent black background
            "Bold=1,"
            "BorderStyle=1,"
            "Outline=2,"                 # Thick black outline for readability
            "Shadow=1,"                  # Drop shadow
            "Alignment=2,"               # Bottom center alignment
            "MarginV=30"                 # Bottom margin
            "'"
        ),
        '-c:a', 'copy',                  # Copy audio without re-encoding
        '-preset', 'medium',             # Good balance of speed and quality
        '-crf', '23',                    # Good quality
        '-y',                            # Overwrite output file
        output_file
    ]

    print("🚀 Starting subtitle burning process...")

    try:
        # Run ffmpeg with real-time progress
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor progress
        duration = None
        for line in process.stderr:
            line = line.strip()

            # Extract duration from ffmpeg output
            if "Duration:" in line and duration is None:
                try:
                    duration_str = line.split("Duration: ")[1].split(",")[0]
                    duration_parts = duration_str.split(":")
                    duration = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + float(duration_parts[2])
                    print(f"📏 Video duration: {duration_str}")
                except:
                    pass

            # Show progress
            if "time=" in line:
                try:
                    time_str = line.split("time=")[1].split()[0]
                    time_parts = time_str.split(":")
                    current_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])

                    if duration:
                        progress = (current_time / duration) * 100
                        print(f"\r⏱️  Progress: {progress:.1f}% ({time_str})", end="", flush=True)
                    else:
                        print(f"\r⏱️  Time: {time_str}", end="", flush=True)
                except:
                    pass

        process.wait()
        print()  # New line after progress

        if process.returncode == 0:
            print("✅ Successfully burned subtitles into video!")
            print(f"🎬 Output file: {output_file}")
            print()
            print("🎉 Done! The subtitles are now permanently part of the video.")
            print("📺 They will be visible in any media player, on any device!")
            print("🔍 The subtitles have white text with black outline for maximum readability.")
        else:
            print("❌ Error burning subtitles into video.")
            print("Check that ffmpeg is properly installed and the input files are valid.")

    except FileNotFoundError:
        print("❌ Error: ffmpeg not found. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        if os.path.exists(output_file):
            os.remove(output_file)
            print("🗑️  Cleaned up partial output file.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
