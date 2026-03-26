#!/usr/bin/env python3
"""
Script to create PNG preview frames showing how burned subtitles will look
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

def get_video_duration(video_file):
    """Get video duration in seconds"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', video_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None

def extract_subtitle_preview_frames(video_file, subtitle_file, output_dir="subtitle_previews",
                                  num_frames=5, font_size=20):
    """Extract sample frames with burned subtitles as PNG files"""

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return False

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return False

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get video duration
    duration = get_video_duration(video_file)
    if not duration:
        print("Warning: Could not determine video duration. Using default timestamps.")
        timestamps = [30, 60, 120, 180, 240]  # Default timestamps
    else:
        # Calculate evenly spaced timestamps
        interval = duration / (num_frames + 1)
        timestamps = [interval * (i + 1) for i in range(num_frames)]

    print(f"📹 Video: {video_file}")
    print(f"📝 Subtitles: {subtitle_file}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🖼️  Extracting {num_frames} preview frames...")
    print()

    # Subtitle filter with optimized styling
    subtitle_filter = (
        f"subtitles={subtitle_file}:"
        "force_style='"
        "Fontname=Arial Bold,"
        f"Fontsize={font_size},"
        "PrimaryColour=&HFFFFFF,"    # White text
        "OutlineColour=&H000000,"    # Black outline
        "BackColour=&H80000000,"     # Semi-transparent black background
        "Bold=1,"
        "BorderStyle=1,"
        "Outline=2,"                 # Thick black outline
        "Shadow=1,"                  # Drop shadow
        "Alignment=2,"               # Bottom center
        "MarginV=30"                 # Bottom margin
        "'"
    )

    success_count = 0

    for i, timestamp in enumerate(timestamps, 1):
        output_file = os.path.join(output_dir, f"subtitle_preview_{i:02d}_{int(timestamp)}s.png")

        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),           # Seek to timestamp
            '-i', video_file,                # Input video
            '-vf', subtitle_filter,          # Apply subtitle filter
            '-vframes', '1',                 # Extract only 1 frame
            '-q:v', '2',                     # High quality
            '-y',                            # Overwrite output
            output_file
        ]

        print(f"⏱️  Extracting frame at {int(timestamp//60):02d}:{int(timestamp%60):02d}...", end=" ")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {os.path.basename(output_file)}")
                success_count += 1
            else:
                print(f"❌ Failed")

        except Exception as e:
            print(f"❌ Error: {e}")

    print()
    if success_count > 0:
        print(f"🎉 Successfully extracted {success_count} preview frames!")
        print(f"📂 Check the '{output_dir}' folder to see how your subtitles will look.")
        print("🔍 Open the PNG files to preview the subtitle styling and positioning.")
        return True
    else:
        print("❌ Failed to extract any preview frames.")
        return False

def create_comparison_frames(video_file, subtitle_file, output_dir="subtitle_comparison"):
    """Create before/after comparison frames"""

    os.makedirs(output_dir, exist_ok=True)

    duration = get_video_duration(video_file)
    if duration:
        # Pick a timestamp with likely subtitle content (middle of video)
        timestamp = duration / 2
    else:
        timestamp = 120  # 2 minutes default

    print(f"🔍 Creating before/after comparison at {int(timestamp//60):02d}:{int(timestamp%60):02d}")

    # Extract original frame (without subtitles)
    original_file = os.path.join(output_dir, "original_frame.png")
    cmd_original = [
        'ffmpeg',
        '-ss', str(timestamp),
        '-i', video_file,
        '-vframes', '1',
        '-q:v', '2',
        '-y',
        original_file
    ]

    # Extract frame with subtitles
    subtitle_file_path = os.path.join(output_dir, "with_subtitles.png")
    subtitle_filter = (
        f"subtitles={subtitle_file}:"
        "force_style='"
        "Fontname=Arial Bold,"
        "Fontsize=20,"
        "PrimaryColour=&HFFFFFF,"
        "OutlineColour=&H000000,"
        "BackColour=&H80000000,"
        "Bold=1,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=30"
        "'"
    )

    cmd_subtitle = [
        'ffmpeg',
        '-ss', str(timestamp),
        '-i', video_file,
        '-vf', subtitle_filter,
        '-vframes', '1',
        '-q:v', '2',
        '-y',
        subtitle_file_path
    ]

    try:
        print("📸 Extracting original frame...", end=" ")
        result1 = subprocess.run(cmd_original, capture_output=True)
        if result1.returncode == 0:
            print("✅")
        else:
            print("❌")
            return False

        print("📸 Extracting frame with subtitles...", end=" ")
        result2 = subprocess.run(cmd_subtitle, capture_output=True)
        if result2.returncode == 0:
            print("✅")
            print(f"🎯 Comparison files created in '{output_dir}' folder:")
            print(f"   📄 original_frame.png - Original video frame")
            print(f"   📄 with_subtitles.png - Frame with burned subtitles")
            return True
        else:
            print("❌")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg first.")
        return

    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    subtitle_file = "translate.vtt"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return

    print("🖼️  Subtitle Preview Generator")
    print("=============================")
    print()
    print("This will create PNG preview images showing how burned subtitles will look.")
    print()

    choice = input("Choose preview type:\n1. Multiple sample frames (5 frames at different times)\n2. Before/after comparison (1 frame)\n3. Both\nEnter choice (1, 2, or 3): ").strip()

    if choice in ["1", "3"]:
        print("\n📋 Extracting multiple sample frames...")
        extract_subtitle_preview_frames(video_file, subtitle_file)

    if choice in ["2", "3"]:
        print("\n🔍 Creating before/after comparison...")
        create_comparison_frames(video_file, subtitle_file)

    print("\n🎉 Preview generation complete!")
    print("📁 Check the generated PNG files to see how your subtitles will look.")
    print("💡 If you like the preview, run the full subtitle burning script.")

if __name__ == "__main__":
    main()
