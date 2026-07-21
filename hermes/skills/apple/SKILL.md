---
name: apple
description: "Apple/macOS platform integration — iMessage/SMS via imsg, Apple Reminders via remindctl, Apple Notes via memo, FindMy (devices/AirTags), and macOS desktop automation (screenshots, clicks, keyboard). These skills only load on macOS systems. Load this when the user wants to interact with Apple services or automate macOS — send iMessages, manage Reminders, write Notes, track Apple devices, or drive the macOS UI."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [apple, macos, imessage, reminders, notes, findmy, automation]
    platforms: [macos]
---

# Apple Platform Hub

macOS-only Apple platform skills — sending iMessages, managing Reminders, editing Notes, locating Apple devices via FindMy, and driving the macOS desktop. Each subsection is condensed; full content in `references/<topic>.md`.

## Quick Routing

| Task | Reference |
|------|-----------|
| Send/receive iMessage or SMS | → `references/imessage.md` |
| Add/list/complete Reminders | → `references/apple-reminders.md` |
| Create/search/edit Notes | → `references/apple-notes.md` |
| Track Apple devices / AirTags | → `references/findmy.md` |
| Voice wake word, ASR, TTS, voiceprint | → `references/macos-voice-interaction.md` |
| Drive macOS desktop (screenshot/click/keyboard) | → `references/macos-computer-use.md` |

## Platform Notes

- All skills in this hub require **macOS** as the host OS.
- Most use the system's native Apple frameworks via small CLI wrappers (`memo`, `remindctl`, `imsg`) — no API keys, no OAuth, no sudo.
- macOS privacy prompts (TCC) appear on first use; the user must click Allow.

## Common Patterns

### iMessage — send + read
```bash
imsg send --to "+15551234567" --text "Hello from Hermes"
imsg history --limit 20          # tail recent messages
```
Full CLI + JSON output + chat-id routing: `references/imessage.md`.

### Reminders — list, add, complete
```bash
remindctl list --pending
remindctl add --title "Buy milk" --list "Personal"
remindctl complete <reminder-id>
```
Full flag matrix + iCloud list sync: `references/apple-reminders.md`.

### Notes — search + create
```bash
memo search "meeting notes"
memo new "Project Phoenix" --body "First draft…"
```
Full CRUD + folder routing + rich content: `references/apple-notes.md`.

### FindMy — locate device
```bash
findmy list                       # devices + AirTags
findmy play --device "iPhone 15"  # emit sound
```
Full device map + AirTags + last-seen: `references/findmy.md`.

### macOS automation
```bash
osascript -e 'tell application "Safari" to activate'
# screenshots + click via Quartz Event Services
```
Full pattern (driving UI without API): `references/macos-computer-use.md`.

## When to Prefer a Hub Skill vs. an Inline CLI

- **One-off send/read?** Just run the CLI command directly — no need to load the file.
- **Multi-step Apple workflow (e.g., read iMessage → write Note → set Reminder → reply)?** Load this umbrella so cross-skill coordination stays consistent.
- **macOS UI driving with screenshots + OCR?** Load `references/macos-computer-use.md` — it documents TCC permissions.

## References

| File | Topic |
|------|-------|
| `references/apple-notes.md` | Apple Notes (memo CLI) |
| `references/apple-reminders.md` | Reminders (remindctl CLI) |
| `references/findmy.md` | FindMy |
| `references/imessage.md` | iMessage (imsg CLI) |
| `references/macos-computer-use.md` | macOS desktop automation |
| `references/macos-voice-interaction.md` | Voice wake word, ASR, VAD, TTS, voiceprint |
