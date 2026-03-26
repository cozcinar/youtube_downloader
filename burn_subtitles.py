#!/usr/bin/env python3
"""
Script to burn subtitles directly into video frames using ffmpeg filters
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

def burn_subtitles_into_video(video_file, subtitle_file, output_file=None,
                             font_size=24, font_color="white",
                             background_color="black@0.5", position="bottom"):
    """Burn subtitles directly into video frames"""

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
        output_file = video_path.parent / f"{video_path.stem}_burned_subtitles{video_path.suffix}"

    print(f"Input video: {video_file}")
    print(f"Subtitle file: {subtitle_file}")
    print(f"Output file: {output_file}")
    print(f"Font size: {font_size}")
    print(f"Font color: {font_color}")
    print(f"Background: {background_color}")
    print("Note: Subtitles will be permanently burned into the video.")

    # Determine subtitle position
    if position == "bottom":
        subtitle_position = "(w-text_w)/2:h-text_h-20"
    elif position == "top":
        subtitle_position = "(w-text_w)/2:20"
    elif position == "center":
        subtitle_position = "(w-text_w)/2:(h-text_h)/2"
    else:
        subtitle_position = position  # Custom position

    # Build ffmpeg command with subtitle filter
    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-vf', f"subtitles={subtitle_file}:force_style='Fontsize={font_size},PrimaryColour=&H{get_hex_color(font_color)},BackColour=&H{get_hex_color(background_color)},Outline=1,Shadow=1'",
        '-c:a', 'copy',  # Copy audio without re-encoding
        '-y',            # Overwrite output file
        str(output_file)
    ]

    print(f"\nProcessing (this may take a while)...")
    print("Burning subtitles into video frames...")

    try:
        # Run with progress indication
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Show progress
        for line in process.stdout:
            if "time=" in line:
                # Extract and show progress
                time_part = [part for part in line.split() if part.startswith("time=")]
                if time_part:
                    print(f"\rProgress: {time_part[0]}", end="", flush=True)

        process.wait()
        print()  # New line after progress

        if process.returncode == 0:
            print("✅ Successfully burned subtitles into video!")
            print(f"Output file: {output_file}")
            print("The subtitles are now permanently part of the video image.")
            return True
        else:
            print("❌ Error burning subtitles into video.")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_hex_color(color_name):
    """Convert color name to hex for ffmpeg"""
    colors = {
        'white': 'FFFFFF',
        'black': '000000',
        'yellow': 'FFFF00',
        'red': 'FF0000',
        'green': '00FF00',
        'blue': '0000FF',
        'cyan': '00FFFF',
        'magenta': 'FF00FF'
    }

    # Remove transparency part if present
    base_color = color_name.split('@')[0]
    return colors.get(base_color.lower(), 'FFFFFF')

def burn_with_custom_style(video_file, subtitle_file, output_file=None):
    """Burn subtitles with custom styling optimized for readability"""

    if output_file is None:
        video_path = Path(video_file)
        output_file = video_path.parent / f"{video_path.stem}_burned_subtitles{video_path.suffix}"

    print(f"Burning subtitles with custom styling...")
    print(f"Input: {video_file}")
    print(f"Subtitles: {subtitle_file}")
    print(f"Output: {output_file}")

    # Advanced subtitle filter with custom styling
    subtitle_filter = (
        f"subtitles={subtitle_file}:"
        "force_style='"
        "Fontname=Arial,"
        "Fontsize=22,"
        "PrimaryColour=&HFFFFFF,"  # White text
        "SecondaryColour=&HFFFFFF,"
        "OutlineColour=&H000000,"  # Black outline
        "BackColour=&H80000000,"   # Semi-transparent black background
        "Bold=1,"
        "Italic=0,"
        "Underline=0,"
        "StrikeOut=0,"
        "ScaleX=100,"
        "ScaleY=100,"
        "Spacing=0,"
        "Angle=0,"
        "BorderStyle=1,"
        "Outline=2,"               # Thick outline for readability
        "Shadow=1,"                # Drop shadow
        "Alignment=2,"             # Bottom center
        "MarginL=10,"
        "MarginR=10,"
        "MarginV=20"               # Bottom margin
        "'"
    )

    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-vf', subtitle_filter,
        '-c:a', 'copy',
        '-y',
        str(output_file)
    ]

    print("\nProcessing with advanced styling...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully burned subtitles with custom styling!")
            print(f"Output file: {output_file}")
            return True
        else:
            print("❌ Error burning subtitles:")
            print(f"FFmpeg error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""

    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed. Please install ffmpeg first.")
        print("On macOS: brew install ffmpeg")
        print("On Ubuntu: sudo apt install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html")
        return

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

    print("Burn Subtitles Into Video")
    print("========================")
    print()
    print("This will permanently burn the subtitles into the video frames.")
    print("The subtitles will be visible in any media player.")
    print("Note: This process may take several minutes depending on video length.")
    print()

    # Ask user for styling preference
    choice = input("Choose styling method:\n1. Custom optimized styling (recommended)\n2. Basic styling\nEnter choice (1 or 2): ").strip()

    if choice == "2":
        # Basic styling with user options
        font_size = input("Enter font size (default: 24): ").strip() or "24"
        font_color = input("Enter font color (white/yellow/red/green/blue, default: white): ").strip() or "white"

        success = burn_subtitles_into_video(
            video_file,
            subtitle_file,
            output_file,
            int(font_size),
            font_color
        )
    else:
        # Custom optimized styling
        success = burn_with_custom_style(video_file, subtitle_file, output_file)

    if success:
        print(f"\n🎉 Success! Your video with burned subtitles is ready:")
        print(f"📁 {output_file}")
        print("\nThe subtitles are now permanently part of the video and will show in any player!")
    else:
        print("\n❌ Failed to burn subtitles into video.")

if __name__ == "__main__":
    main()
