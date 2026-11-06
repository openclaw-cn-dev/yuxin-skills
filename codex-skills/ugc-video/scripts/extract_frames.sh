#!/usr/bin/env bash
# Extract frames from a video for frame-by-frame teardown.
# Usage: extract_frames.sh <video> [output_dir]
# Output:
#   <out>/hook/      frames every 0.25s for the first 3 seconds
#   <out>/body/      one frame per second for the rest of the video
#   <out>/scenes/    frames at detected scene cuts (with timestamps in scenes.txt)
#   <out>/audio.wav  mono 16 kHz audio for transcription
#   <out>/info.txt   duration, resolution, fps
set -euo pipefail

VIDEO="${1:?Usage: extract_frames.sh <video> [output_dir]}"
OUT="${2:-teardown_$(basename "${VIDEO%.*}")}"
mkdir -p "$OUT/hook" "$OUT/body" "$OUT/scenes"

ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate:format=duration \
  -of default=noprint_wrappers=1 "$VIDEO" > "$OUT/info.txt"

# First 3 seconds, 4 frames per second
ffmpeg -v error -y -t 3 -i "$VIDEO" -vf "fps=4,scale=540:-2" "$OUT/hook/hook_%03d.jpg"

# Rest of the video, 1 frame per second (body_NNN is about 3 + NNN - 1 seconds into the video)
ffmpeg -v error -y -ss 3 -i "$VIDEO" -vf "fps=1,scale=540:-2" "$OUT/body/body_%03d.jpg"

# Scene cuts
ffmpeg -v info -y -i "$VIDEO" \
  -vf "select='gt(scene,0.3)',showinfo,scale=540:-2" -vsync vfr \
  "$OUT/scenes/scene_%03d.jpg" 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$OUT/scenes.txt" || true

# Audio for transcription (skipped if the video has no audio track)
ffmpeg -v error -y -i "$VIDEO" -vn -ac 1 -ar 16000 "$OUT/audio.wav" 2>/dev/null || echo "no audio track" > "$OUT/audio_missing.txt"

echo "Frames written to $OUT"
