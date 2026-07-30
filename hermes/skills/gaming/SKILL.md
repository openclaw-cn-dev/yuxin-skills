---
name: gaming
description: "Set up and manage game servers, modpacks, and emulator-based gameplay — Minecraft server hosting and Pokemon gameplay via headless emulator."
version: 1.0.0
author: Hermes Agent (consolidation)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [gaming, minecraft, pokemon, server, emulator, modpack, pyboy]
---

# Gaming

Unified entry point for game server management and emulator-based gameplay.
Covers two domains: hosting modded Minecraft servers, and playing Pokemon via
headless emulation with RAM reads.

## When to Use

- User wants to set up a modded Minecraft server from a server pack
- User wants to play Pokemon via headless emulation
- User asks about PyBoy, NeoForge/Forge, CurseForge, Modrinth
- User references game server performance tuning or backups
- User mentions ROM files (.gb, .gbc, .gba) for Pokemon

## Minecraft Modpack Server

Host modded Minecraft servers from CurseForge or Modrinth server packs.

### Quick Start

```bash
mkdir -p ~/minecraft-server && cd ~/minecraft-server
wget -O serverpack.zip "<URL>"
unzip -o serverpack.zip -d server
cd server
# Install Java 21 (1.21+) or Java 17 (1.18-1.20)
# Set INSTALL_ONLY=true for first run, e.g.:
ATM10_INSTALL_ONLY=true bash startserver.sh
echo "eula=true" > eula.txt
```

### Key Config

- `allow-flight=true` — REQUIRED for modded (jetpacks, flying mounts)
- `max-tick-time=180000` — modded needs longer tick timeout
- `online-mode=false` for LAN without Mojang auth (set `enforce-secure-profile=false` too)
- RAM: 100-200 mods → 6-12GB, 200-350+ mods → 12-24GB
- First startup is SLOW (several minutes for big packs) — don't panic
- `pgrep -fa neoforge` to check if running; look for "Done!" in `logs/latest.log`
- Set up automated backups via hourly cron + tar.gz (keep last 24)

### JVM Args (G1GC-tuned)

```
-Xms12G -Xmx24G -XX:+UseG1GC -XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15
```

## Pokemon Player

Play Pokemon Red/Blue/Yellow via headless emulation using the `pokemon-agent`
package (PyBoy-based). RAM reads for state, vision for spatial awareness.

### Prerequisites

- Repo: `NousResearch/pokemon-agent` on GitHub (Python 3.10+, uv or venv)
- ROM file required — NEVER download or provide ROMs; ask the user
- GPU not required, runs CPU-only

### Startup

```bash
cd pokemon-agent && source .venv/bin/activate
pokemon-agent serve --rom roms/pokemon_red.gb --port 9876 &
# Wait 4s for startup, verify:
curl http://localhost:9876/health
```

### Gameplay Loop

1. **OBSERVE** — GET `/state` (position, HP, battle, dialog) + GET `/screenshot` → vision_analyze
2. **ORIENT** — dialog > battle > heal > objective > training > explore
3. **DECIDE** — priority: dialog > battle > heal > story > training > explore
4. **ACT** — POST `/action` with 2-4 actions max (NOT 10-15)
5. **VERIFY** — screenshot after every move sequence
6. **SAVE** — POST `/save` with descriptive name every 15-20 turns, before risky fights

### Critical Tips

- **Use vision constantly** — RAM state tells position/HP, NOT what's around you
- **Warp transitions need extra wait** — add 2-3 `wait_60` after doors/stairs
- **Building exit trap** — you appear IN FRONT of the door; sidestep before going north
- **Ledges are one-way** — jump DOWN only, find gaps to go around
- **Gen 1 quirks**: Psychic is OP (Ghost bugged), crits based on Speed, Wrap/Bind prevent action
- **Battle**: FIGHT is top-left (default), RUN is bottom-right (down+right)

### Memory Convention

```
PKM:OBJECTIVE, PKM:MAP, PKM:STRATEGY, PKM:PROGRESS, PKM:STUCK, PKM:TEAM
```
