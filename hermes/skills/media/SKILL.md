---
name: media
description: "Media content tools — YouTube transcripts to summaries/threads/blogs, GIF search via Tenor, Spotify play/search/playlist mgmt, Suno-like song generation from lyrics+tags (HeartMuLa), and audio spectrograms/features (mel/chroma/MFCC). Load when the user wants to interact with audio or video content: fetch a YouTube transcript, find a GIF, play Spotify, generate a song, or analyze audio."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [media, youtube, gif, spotify, audio, music, transcript]
---

# Media Content Hub

Audio + video + image content tooling — YouTube transcripts, GIF search, Spotify control, AI music generation, and audio analysis. Each subsection is condensed; full content in `references/<topic>.md`.

## Quick Routing

| Task | Reference |
|------|-----------|
| YouTube transcript → summary / thread / blog | → `references/youtube-content.md` |
| Search/download a GIF from Tenor | → `references/gif-search.md` |
| Play, search, queue, manage Spotify | → `references/spotify.md` |
| Generate a song from lyrics + tags (Suno-like) | → `references/heartmula.md` |
| Audio spectrograms / mel / chroma / MFCC | → `references/songsee.md` |

## Common Patterns

### YouTube — Transcript → Thread
```bash
python scripts/youtube-fetch-transcript.py <video-id-or-url> > transcript.txt
# then summarize, thread, or repurpose
```
Output format reference: `references/youtube-output-formats.md`.

### GIF Search
```bash
curl 'https://api.tenor.com/v2/search?q=cat&limit=10' -H "Authorization: $TENOR_API_KEY" | jq '.results[].media[0].gif.url'
```

### Spotify
```bash
spotify play "Beat It"
spotify search "Daft Punk"
spotify device list
```

### HeartMuLa — Song Generation
```bash
heartmula generate --lyrics lyrics.txt --tags "pop,female,major-key" --out out.wav
```

### SongSee — Audio Features
```bash
songsee mel    input.wav --out mel.png
songsee mfcc   input.wav --out mfcc.json
```

## When to Use This Hub

- **Audio/video/image workflows that touch multiple services** → load this umbrella so cross-service consistency is preserved.
- **One-shot CLI (e.g., "search me a cat gif")** → run the CLI directly.
- **Cross-modal generation** (lyrics → audio → visualization) → load `references/heartmula.md` + `references/songsee.md`.

## Scripts

- `scripts/youtube-fetch-transcript.py` — fetch YouTube transcript by video ID or URL.

## References

| File | Topic |
|------|-------|
| `references/youtube-content.md` | YouTube transcripts + repurposing |
| `references/gif-search.md` | Tenor GIF search |
| `references/spotify.md` | Spotify CLI control |
| `references/heartmula.md` | HeartMuLa song generation |
| `references/songsee.md` | Audio spectrogram analysis |
| `references/youtube-output-formats.md` | YouTube transcript output formats |
