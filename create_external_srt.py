#!/usr/bin/env python3
"""
Create external SRT subtitle file that auto-loads with video
"""

import os
import re

def convert_vtt_to_srt(vtt_file, srt_file):
    """Convert VTT subtitle file to SRT format"""
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove WEBVTT header
        content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.MULTILINE | re.DOTALL)

        # Split into blocks
        blocks = re.split(r'\n\n+', content.strip())

        srt_lines = []
        subtitle_number = 1

        for block in blocks:
            if not block.strip():
                continue

            lines = block.strip().split('\n')

            # Skip cue identifiers (like "cue-4")
            if len(lines) >= 2 and '-->' in lines[1]:
                timestamp_line = lines[1]
                text_lines = lines[2:]
            elif len(lines) >= 1 and '-->' in lines[0]:
                timestamp_line = lines[0]
                text_lines = lines[1:]
            else:
                continue

            if not text_lines:
                continue

            # Convert timestamp format: 00:01:14.899 --> 00:01:20.219
            # to SRT format: 00:01:14,899 --> 00:01:20,219
            srt_timestamp = timestamp_line.replace('.', ',')

            # Add subtitle number
            srt_lines.append(str(subtitle_number))

            # Add timestamp
            srt_lines.append(srt_timestamp)

            # Add text lines
            for text_line in text_lines:
                if text_line.strip():  # Skip empty lines
                    srt_lines.append(text_line.strip())

            # Add empty line between subtitles
            srt_lines.append('')

            subtitle_number += 1

        # Write SRT file
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_lines))

        return True

    except Exception as e:
        print(f"Error converting VTT to SRT: {e}")
        return False

def main():
    vtt_file = "translate.vtt"
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    srt_file = "GUZELYURT ATIK SU ARITMA TESİSİ.srt"  # Same name as video for auto-loading

    if not os.path.exists(vtt_file):
        print(f"Error: {vtt_file} not found.")
        return

    print(f"Converting {vtt_file} to {srt_file}...")
    print("This will create an external subtitle file that auto-loads with your video.")

    if convert_vtt_to_srt(vtt_file, srt_file):
        print(f"✅ Successfully created: {srt_file}")
        print()
        print("How to use:")
        print(f"1. Keep {srt_file} in the same folder as {video_file}")
        print("2. Most media players will automatically load the subtitles")
        print("3. If not, manually load the .srt file in your media player")
        print()
        print("Supported players: VLC, MPV, Windows Media Player, QuickTime, etc.")
    else:
        print("❌ Failed to convert subtitles.")

if __name__ == "__main__":
    main()
