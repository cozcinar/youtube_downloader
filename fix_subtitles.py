#!/usr/bin/env python3
"""
Script to fix subtitle display issues by converting VTT to SRT and using better embedding
"""

import os
import subprocess
import re

def convert_vtt_to_srt(vtt_file, srt_file):
    """Convert VTT subtitle file to SRT format"""
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        # Split into cues
        cues = re.split(r'\n\n+', vtt_content.strip())

        srt_content = []
        cue_number = 1

        for cue in cues:
            lines = cue.strip().split('\n')
            if len(lines) < 2:
                continue

            # Skip WEBVTT header and NOTE lines
            if lines[0].startswith('WEBVTT') or lines[0].startswith('NOTE') or lines[0].startswith('cue-'):
                continue

            # Find timestamp line
            timestamp_line = None
            text_lines = []

            for i, line in enumerate(lines):
                if '-->' in line:
                    timestamp_line = line
                    text_lines = lines[i+1:]
                    break

            if not timestamp_line or not text_lines:
                continue

            # Convert WebVTT timestamp to SRT format
            # WebVTT: 00:01:14.899 --> 00:01:20.219
            # SRT: 00:01:14,899 --> 00:01:20,219
            srt_timestamp = timestamp_line.replace('.', ',')

            # Add cue number, timestamp, and text
            srt_content.append(str(cue_number))
            srt_content.append(srt_timestamp)
            srt_content.extend(text_lines)
            srt_content.append('')  # Empty line between cues

            cue_number += 1

        # Write SRT file
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

        print(f"✅ Converted {vtt_file} to {srt_file}")
        return True

    except Exception as e:
        print(f"❌ Error converting VTT to SRT: {e}")
        return False

def add_subtitles_with_srt(video_file, srt_file, output_file):
    """Add SRT subtitles to video with better compatibility"""

    print(f"Adding SRT subtitles to: {video_file}")
    print(f"Subtitle file: {srt_file}")
    print(f"Output: {output_file}")

    # Method 1: Try with mov_text codec and forced display
    cmd1 = [
        'ffmpeg',
        '-i', video_file,
        '-i', srt_file,
        '-map', '0:v',
        '-map', '0:a',
        '-map', '1:s',
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-c:s', 'mov_text',
        '-metadata:s:s:0', 'language=eng',
        '-metadata:s:s:0', 'title=English',
        '-disposition:s:0', 'default+forced',  # Force display
        '-y',
        output_file
    ]

    print("\nTrying method 1: mov_text with forced display...")

    try:
        result = subprocess.run(cmd1, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully added subtitles (method 1)!")
            return True
        else:
            print("Method 1 failed, trying method 2...")

            # Method 2: Try with subrip codec
            cmd2 = [
                'ffmpeg',
                '-i', video_file,
                '-i', srt_file,
                '-map', '0:v',
                '-map', '0:a',
                '-map', '1:s',
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-c:s', 'subrip',
                '-metadata:s:s:0', 'language=eng',
                '-metadata:s:s:0', 'title=English',
                '-disposition:s:0', 'default',
                '-y',
                output_file
            ]

            print("Trying method 2: subrip codec...")

            result2 = subprocess.run(cmd2, capture_output=True, text=True)

            if result2.returncode == 0:
                print("✅ Successfully added subtitles (method 2)!")
                return True
            else:
                print("❌ Both methods failed:")
                print(f"Method 1 error: {result.stderr}")
                print(f"Method 2 error: {result2.stderr}")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_external_srt():
    """Create external SRT file that can be loaded separately"""
    vtt_file = "translate.vtt"
    srt_file = "GUZELYURT ATIK SU ARITMA TESİSİ.srt"

    if not os.path.exists(vtt_file):
        print(f"Error: {vtt_file} not found.")
        return False

    print("Creating external SRT subtitle file...")

    if convert_vtt_to_srt(vtt_file, srt_file):
        print(f"✅ Created external subtitle file: {srt_file}")
        print("\nTo use external subtitles:")
        print("1. Place the .srt file in the same folder as your video")
        print("2. Make sure they have the same base name")
        print("3. Most media players will auto-load the subtitles")
        print("\nAlternatively, you can manually load the .srt file in your media player.")
        return True

    return False

def main():
    video_file = "GUZELYURT ATIK SU ARITMA TESİSİ.mp4"
    vtt_file = "translate.vtt"
    srt_file = "translate.srt"
    output_file = "GUZELYURT ATIK SU ARITMA TESİSİ_with_srt_subtitles.mp4"

    # Check if files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        return

    if not os.path.exists(vtt_file):
        print(f"Error: Subtitle file '{vtt_file}' not found.")
        return

    print("Subtitle Display Fix")
    print("===================")
    print()

    # Step 1: Convert VTT to SRT
    print("Step 1: Converting VTT to SRT format...")
    if not convert_vtt_to_srt(vtt_file, srt_file):
        return

    # Step 2: Embed SRT subtitles
    print("\nStep 2: Embedding SRT subtitles...")
    if add_subtitles_with_srt(video_file, srt_file, output_file):
        print(f"\n✅ Success! Video with subtitles: {output_file}")
        print("\nIf subtitles still don't show automatically:")
        print("1. Try different media players (VLC, MPV, etc.)")
        print("2. Check subtitle settings in your media player")
        print("3. Use the external .srt file created alongside")
    else:
        print("\n⚠️  Embedding failed, but you can use the external SRT file.")

    # Step 3: Create external SRT as backup
    print("\nStep 3: Creating external SRT file as backup...")
    create_external_srt()

    # Clean up temporary SRT
    try:
        if os.path.exists(srt_file) and srt_file != "GUZELYURT ATIK SU ARITMA TESİSİ.srt":
            os.remove(srt_file)
    except:
        pass

if __name__ == "__main__":
    main()
