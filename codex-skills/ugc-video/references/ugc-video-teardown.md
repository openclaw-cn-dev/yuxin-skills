
# UGC Video Teardown → New Scripts

## Goal

Turn one video into (1) a precise second-by-second breakdown of why it works or fails and (2) several new, original scripts that reuse the structure, not the content.

## Before you start: gather context

- The video file (MP4, MOV). If only a link is given, ask the user to upload the file.
- Whose video it is (own ad, competitor, organic creator post) and its results if known (views, CTR, CPA)
- The user's product, offer and audience for the new scripts

## Step 1: Extract frames and audio

If a shell with ffmpeg is available, run:

```bash
bash scripts/extract_frames.sh <video> <output_dir>
```

This produces dense frames for the first 3 seconds (every 0.25 s), one frame per second for the rest, frames at scene cuts with timestamps, and an audio file. View the frames in order. Transcribe the audio with whatever transcription tool is available; if none is, ask the user for the script or captions, or rely on on-screen text.

If no shell is available, analyze the video directly if the model can view it, or ask the user for screenshots of key moments plus the transcript.

## Step 2: Hook analysis (0–3 s), the most important part

Check frame by frame:

- **Conflict**: is there dramatic conflict in the first 3 seconds (person vs problem, person vs person, expectation vs reality, stakes and a ticking clock)? No conflict means weak stopping power and weak retention. This is the first thing to report.
- First frame: what does the viewer see before any sound? Is there motion, a face, an unexpected object?
- First spoken words and first on-screen text
- When does the product first appear?

## Step 3: Full breakdown

Build a timeline table, one row per beat or cut:

| Time | Shot / visual | Camera (close-up, POV, wide) | Spoken line | On-screen text | Sound / music | Purpose (hook, conflict, problem, demo, proof, CTA) |

Then summarize:
- Structure pattern (for example conflict → escalation → product reveal → proof → CTA)
- Pacing: number of cuts, average shot length
- Retention devices: open loops, questions, pattern interrupts, payoff timing
- Proof and CTA: what makes the claim believable, how the ask is made
- Weak points and what to fix

## Step 4: Generate new scripts

Write 3 new scripts for the user's product that keep the winning structure and pacing but use new situations, lines and visuals:

- Every script opens with a clear conflict in the first 3 seconds.
- Give each script 3 alternative conflict hooks.
- Use the timeline table format so it can be filmed directly.
- Follow `references/ugc-video-scripts.md` for the creator brief and `paid-ads` (`references/ad-policy-compliance.md`) for claims.

## Rules

- Reuse patterns, never content. Do not copy another brand's lines, footage, characters, music or brand names.
- Do not reproduce a competitor's video shot for shot; change the situation and the conflict.
- Base claims in new scripts on the user's real product facts.

## Output format

1. Hook verdict: conflict present? score 1–5, and why
2. Timeline breakdown table
3. Pattern summary and weak points
4. Three new scripts with three conflict hooks each
5. Suggested test order
