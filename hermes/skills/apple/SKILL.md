---
name: apple
description: "Apple/macOS-specific skills — iMessage, Reminders, Notes, FindMy, and macOS automation. These skills only load on macOS systems."
version: 1.0.0
author: Hermes Agent (consolidation)
platforms: [macos]
metadata:
  hermes:
    tags: [apple, macos, imessage, reminders, notes, findmy, automation, accessibility]
---

# Apple / macOS Skills

Unified entry point for all Apple-specific and macOS-only skills. These skills
use native macOS tools/CLIs and are only available on macOS systems — do not
attempt to use them on Linux or Windows.

## Quick Start

Most Apple skills are installed by Hermes Agent by default. Check availability:
```bash
which imsg     # iMessage/SMS
which memo     # Apple Notes
# FindMy.app is built-in on macOS
```

## Skills Overview

### Apple Notes (`memo` CLI)

Manage Apple Notes via the `memo` CLI — create, search, edit, and manage notes
from the terminal without opening the Notes app.

**Install:** `brew install memochou/tap/memo` (or `pip install memo`)

Basic commands:
```bash
memo list                    # List recent notes
memo search "keyword"        # Search across all notes
memo show <id>               # Read a specific note
memo create "Title" "Body"   # Create a new note
memo edit <id> "New text"    # Update a note
memo delete <id>             # Delete a note
```

Common issues:
- macOS must be running and logged in (Notes app uses CloudKit)
- The `memo` CLI needs Full Disk Access in System Preferences
- iCloud sync may cause delays — notes may not appear immediately

### FindMy (Device Tracking)

Track Apple devices, AirTags, and FindMy network accessories via `FindMy.app` on
macOS. Query device location, battery, and status.

**Location query:**
```bash
# List all devices
findmy devices

# Get location for a specific device
findmy locate "Hua's iPhone"

# Get last known location (from cache, no live query)
findmy last-known "Hua's AirPods"
```

**Item tracking (AirTags):**
```bash
# List all items
findmy items

# Locate a specific item
findmy item locate "Keys"

# Play a sound on an AirTag
findmy item sound "Backpack"
```

**Person tracking (family sharing):**
```bash
# List people sharing location
findmy friends

# Locate a person
findmy locate "Family Member Name"
```

Important:
- FindMy.app must be installed and signed in with an Apple ID
- Live location queries may take 5-15 seconds
- AirTag precision finding works only on U1-equipped iPhones
- Cached locations (from `last-known`) may be stale — the tool returns a timestamp
- First-time usage requires macOS location permission grant

### iMessage (`imsg` CLI)

Send and receive iMessages and SMS via the `imsg` CLI on macOS. Uses the
Messages app's database — no additional auth needed.

**Install:** `brew install imsg`

Basic commands:
```bash
# Send a message
imsg send "+15551234567" "Hello from terminal"

# Read recent conversations
imsg chats

# Read messages from a contact
imsg read "+15551234567"

# Search messages
imsg search "meeting tomorrow"
```

Important:
- Must be signed into Messages app with an Apple ID
- SMS requires iPhone relay (continuity)
- The Messages app must be running or have been recently used
- Message sending may prompt for permission on first use

### macOS Computer Use

Drive the macOS desktop programmatically in the background — take screenshots,
click, type, and automate GUI interactions using AppleScript and accessibility
APIs. Useful for automating desktop apps, testing GUI workflows, and interacting
with applications that lack CLI interfaces.

**Core operations:**
```bash
# Screenshot the entire desktop
screencapture /tmp/desktop.png

# Screenshot a specific window
screencapture -l <window-id> /tmp/window.png

# Run AppleScript
osascript -e 'tell application "Finder" to get name of every window'
```

**Accessibility automation (requires permission grant):**
- System Preferences → Security & Privacy → Privacy → Accessibility
- Grant permission to Terminal.app or your automation tool
- Use `osascript` for AppleScript automation
- Use `cliclick` or `xdotool` for simulated mouse/keyboard input

**Window management:**
```bash
# List all windows
osascript -e 'tell application "System Events" to get name of every window of every process'

# Get frontmost app
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'
```

**Pitfalls:**
- macOS 14+ requires explicit screen recording permission for `screencapture` in some contexts
- Accessibility permission may reset after macOS updates
- AppleScript sandboxing can prevent automation of certain apps
- GUI automation is inherently fragile — prefer CLI tools when available
- ALWAYS verify screenshots after `screencapture` — black/blank screenshots mean permission denied

## When NOT to Use

- On non-macOS systems — these skills won't work
- When a CLI or API alternative exists that is cross-platform
- For sending messages when the user has a messaging platform already wired into Hermes (use `send_message` instead of `imsg`)
