---
name: media
description: Media content skills — audio, video, GIF, and music generation / inspection tools. Load when you need to pick a media format (Spotify playback, YouTube transcripts, GIF search, audio spectrograms, music generation).
version: 1.0.0
metadata:
  hermes:
    tags: [media, audio, video, gif, music, spotify, youtube]
---

# Media Skills

Class-level umbrella for audio / video / music / GIF tools.

## Children

- `spotify/` — Spotify: play, search, queue, manage playlists and devices.
- `youtube-content/` — YouTube transcripts → summaries, threads, blogs.
- `gif-search/` — Search/download GIFs from Tenor via curl + jq.
- `songsee/` — Audio spectrograms / features (mel, chroma, MFCC) via CLI.
- `heartmula/` — HeartMuLa: Suno-like song generation from lyrics + tags.

## How to choose

- **Play music / control Spotify** → `spotify/`
- **Summarize a YouTube video** → `youtube-content/`
- **Find a GIF for a chat** → `gif-search/`
- **Analyze audio frequencies** → `songsee/`
- **Generate music from lyrics** → `heartmula/`
