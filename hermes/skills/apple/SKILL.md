---
name: apple
description: Operate native macOS Apple apps and services from a terminal — Notes, Reminders, FindMy, iMessage, and macOS computer-use automation. Load this umbrella when you need to pick the right Apple app skill.
version: 1.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, findmy, imessage, icloud, automation]
---

# Apple Apps & Services (macOS)

Class-level umbrella for operating native macOS Apple apps from a terminal. All skills sync via iCloud to your other Apple devices (iPhone, iPad) unless noted.

## Platform requirement

**macOS only.** Every child skill requires macOS with the relevant Apple app installed and iCloud signed in.

## Children (pick one)

- `apple-ecosystem/` — Cross-app overview: how Notes, Reminders, FindMy, and iMessage integrate. Read first.
- `apple-notes/` — Manage Apple Notes via the `memo` CLI: create, search, edit.
- `apple-reminders/` — Apple Reminders via `remindctl`: add, list, complete.
- `findmy/` — Track Apple devices / AirTags via FindMy.app.
- `imessage/` — Send and receive iMessages / SMS via the `imsg` CLI.
- `macos-computer-use/` — Drive the macOS desktop (screenshots, clicks, typing) in the background.

## How to choose

- **Just want to send a text or read a message** → `imessage/`
- **Capture a quick note** → `apple-notes/`
- **Add a todo or reminder** → `apple-reminders/`
- **Locate a device** → `findmy/`
- **Need to drive a macOS UI without API** → `macos-computer-use/`
- **Need the cross-app overview** → `apple-ecosystem/`
