---
name: module
description: Reusable application modules — drop-in components for common needs (auth, etc.) that can be copied into a project and adapted. Load when you need a starting point for a common application module.
version: 1.0.0
metadata:
  hermes:
    tags: [module, reusable, auth, fastapi, vue3]
---

# Reusable Application Modules

Class-level umbrella for **drop-in application modules** — pre-built components you can copy into a project and adapt. Each child is a self-contained module.

## Children

- `auth-module/` — Reusable user authentication: FastAPI backend + Vue3 frontend (registration / login / JWT / session).

## How to use

1. Load the child skill matching your need.
2. Copy the code/config into your project.
3. Apply any project-specific patches described in `references/integration-notes.md` (where available).
