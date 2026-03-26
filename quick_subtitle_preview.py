#!/usr/bin/env python3
"""
Quick script to create PNG previews of burned subtitles
"""

import os
import subprocess

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    subtitle_file = "translate.vtt"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file '{subtitle_file}' not found.")
        return

    # Create output directory
    output_dir = "subtitle_previews"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🖼️  Creating subtitle preview images...")
    print(f"📁 Output folder: {output_dir}")
    print()

    # Sample timestamps to extract (in seconds)
    timestamps = [60, 120, 180, 240, 300]  # 1min, 2min, 3min, 4min, 5min

    # Subtitle filter with the same styling as the burn script
    subtitle_filter = (
        f"subtitles={subtitle_file}:"
        "force_style='"
        "Fontname=Arial Bold,"
        "Fontsize=20,"
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
        minutes = timestamp // 60
        seconds = timestamp % 60
        output_file = os.path.join(output_dir, f"preview_{i}_{int(minutes):02d}m{int(seconds):02d}s.png")

        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),           # Seek to timestamp
            '-i', video_file,                # Input video
            '-vf', subtitle_filter,          # Apply subtitle filter
            '-vframes', '1',                 # Extract only 1 frame
            '-q:v', '2',                     # High quality PNG
            '-y',                            # Overwrite output
            output_file
        ]

        print(f"📸 Extracting frame at {int(minutes):02d}:{int(seconds):02d}...", end=" ")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {os.path.basename(output_file)}")
                success_count += 1
            else:
                print(f"❌ Failed (no subtitle at this time?)")

        except Exception as e:
            print(f"❌ Error: {e}")

    print()

    if success_count > 0:
        print(f"🎉 Successfully created {success_count} preview images!")
        print(f"📂 Open the '{output_dir}' folder to see the PNG files")
        print("🔍 These show exactly how the burned subtitles will look:")
        print("   • White text with black outline")
        print("   • Positioned at bottom center")
        print("   • Semi-transparent background")
        print()
        print("💡 If you like the preview, run: python burn_translate_subtitles.py")
    else:
        print("❌ No preview images were created.")
        print("💡 Try different timestamps or check if subtitles exist at those times.")

if __name__ == "__main__":
    main()
