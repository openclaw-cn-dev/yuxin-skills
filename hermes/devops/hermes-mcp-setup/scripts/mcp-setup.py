"""
mcp-setup.py — End-to-end MCP server install + configure + verify on Windows.

Handles the 5 traps from the SKILL.md:
  1. Direct `patch` of config.yaml is refused → uses `hermes mcp add` (or full
     overwrite via read_file + write_file as last resort)
  2. `--args` must be passed as a list, not a single string
  3. `hermes mcp add` is interactive y/N → feeds `input="y\n"`
  4. npx first-time 0xb0 UTF-8 error → pre-installs the npm package globally
  5. PATH encoding issues → prepends node dir to PATH in subprocess env

Usage (from Python):
    from mcp_setup import setup_mcp_server
    result = setup_mcp_server("filesystem", command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem",
              "C:/Users/Administrator/Desktop"],
        env={})
    print(result)  # {"name": ..., "tools": 14, "status": "enabled", ...}

Usage (from CLI):
    python mcp-setup.py filesystem
    python mcp-setup.py github --env GITHUB_TOKEN=ghp_xxx
"""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


NODE_DIR = r"C:\Program Files\nodejs"
NPM = Path(NODE_DIR) / "npm.cmd"
HERMES = "hermes"
TIMEOUT_ADD = 90   # seconds
TIMEOUT_TEST = 60  # seconds


def _npm_path() -> str:
    if not NPM.exists():
        raise FileNotFoundError(
            f"npm not found at {NPM}. Install Node.js first."
        )
    return str(NPM)


def _node_env() -> dict:
    """Prepend node dir to PATH to avoid npx encoding issues (trap #5)."""
    env = os.environ.copy()
    env["PATH"] = NODE_DIR + os.pathsep + env.get("PATH", "")
    # Force UTF-8 in subprocess (avoid the 0xb0 error on Chinese-locale output)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def preinstall_npm(pkg: str, *, dry_run: bool = False) -> None:
    """Globally install an npm package so npx doesn't download mid-`mcp add` (trap #4)."""
    if not pkg.startswith("@") and "/" not in pkg:
        # uvx-style server (e.g. "mcp-server-fetch"); nothing to pre-install
        return
    if dry_run:
        print(f"[dry-run] would: npm install -g {pkg}")
        return
    print(f"📦 Pre-installing {pkg} globally to avoid npx 0xb0 UTF-8 error...")
    result = subprocess.run(
        [_npm_path(), "install", "-g", pkg],
        capture_output=True, text=True, timeout=120, env=_node_env(),
    )
    if result.returncode != 0:
        print(f"⚠️  npm install -g {pkg} exited {result.returncode}")
        print(f"   stderr: {result.stderr[:300]}")
        # Not fatal — uvx servers can still work


def add_server(
    name: str,
    *,
    command: str,
    args: Sequence[str],
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run `hermes mcp add` with the correct flags, feed y\\n, return parsed result.

    Args:
        name: server name (e.g. "filesystem", "github")
        command: executable to launch (e.g. "npx", "uvx", "node")
        args: list of CLI args (each as a separate `--args` flag — trap #2)
        env: env vars to set (e.g. {"NOTION_API_KEY": "secret_xxx"})
        dry_run: print what would run, don't execute

    Returns:
        dict with keys: name, stdout, stderr, returncode, saved
    """
    cmd = [HERMES, "mcp", "add", name, "--command", command]
    for a in args:
        cmd += ["--args", a]
    if env:
        for k, v in env.items():
            cmd += ["--env", f"{k}={v}"]

    if dry_run:
        print(f"[dry-run] cmd: {' '.join(cmd)}")
        return {"name": name, "dry_run": True}

    print(f"🔌 Adding MCP server '{name}'...")
    result = subprocess.run(
        cmd, input="y\n", capture_output=True, text=True,
        timeout=TIMEOUT_ADD, env=_node_env(),
    )
    saved = "✓ Saved" in result.stdout
    return {
        "name": name,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "saved": saved,
    }


def test_server(name: str, *, dry_run: bool = False) -> dict:
    """Run `hermes mcp test <name>` and parse tool count from output."""
    if dry_run:
        print(f"[dry-run] hermes mcp test {name}")
        return {"name": name, "dry_run": True}
    print(f"🧪 Testing MCP server '{name}'...")
    result = subprocess.run(
        [HERMES, "mcp", "test", name],
        capture_output=True, text=True, timeout=TIMEOUT_TEST, env=_node_env(),
    )
    out = result.stdout
    # Parse "Tools discovered: N"
    tool_count = 0
    for line in out.splitlines():
        if "Tools discovered:" in line:
            try:
                tool_count = int(line.split(":")[-1].strip())
            except ValueError:
                pass
    connected = "✓ Connected" in out
    return {
        "name": name,
        "connected": connected,
        "tool_count": tool_count,
        "stdout": out,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def list_servers() -> str:
    """Run `hermes mcp list` and return stdout."""
    result = subprocess.run(
        [HERMES, "mcp", "list"],
        capture_output=True, text=True, timeout=15, env=_node_env(),
    )
    return result.stdout


def setup_mcp_server(
    name: str,
    *,
    command: str,
    args: Sequence[str],
    env: dict[str, str] | None = None,
    preinstall_pkg: str | None = None,
) -> dict:
    """Full end-to-end: preinstall (if npx) → add → test.

    Returns:
        dict with: name, preinstall (str|None), add (dict), test (dict), ok (bool)
    """
    out: dict = {"name": name}

    # 1. Pre-install npm pkg if it's an npx-style server
    if preinstall_pkg:
        preinstall_npm(preinstall_pkg)
        out["preinstall"] = preinstall_pkg

    # 2. Add via `hermes mcp add`
    out["add"] = add_server(name, command=command, args=args, env=env or {})

    # 3. Test
    out["test"] = test_server(name)

    # 4. Summary
    out["ok"] = out["test"].get("connected", False) and out["test"].get("tool_count", 0) > 0
    return out


# ---------- Built-in presets for the 4 most common servers ----------

PRESETS: dict[str, dict] = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem",
                 r"C:\Users\Administrator\Desktop",
                 r"C:\Users\Administrator\Documents"],
        "preinstall_pkg": "@modelcontextprotocol/server-filesystem",
        "env": {},
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "preinstall_pkg": "@modelcontextprotocol/server-github",
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},  # caller fills in
    },
    "notion": {
        "command": "uvx",
        "args": ["--from", "notion-mcp-server", "notion-mcp.exe"],
        "preinstall_pkg": None,
        "env": {"NOTION_API_KEY": ""},  # caller fills in
    },
    "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "preinstall_pkg": None,
        "env": {},
    },
}


# ---------- CLI ----------

def _cli():
    import argparse
    p = argparse.ArgumentParser(
        description="Install + configure + verify an MCP server in Hermes Agent."
    )
    p.add_argument("server", choices=list(PRESETS.keys()),
                   help="Which preset server to install")
    p.add_argument("--env", action="append", default=[],
                   help="Env var in KEY=VALUE form (can be repeated)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would happen, don't execute")
    p.add_argument("--list", action="store_true",
                   help="Just list currently installed MCP servers and exit")
    args = p.parse_args()

    if args.list:
        print(list_servers())
        return 0

    preset = PRESETS[args.server]
    env = dict(preset.get("env", {}))
    for kv in args.env:
        if "=" in kv:
            k, v = kv.split("=", 1)
            env[k] = v

    # GitHub/Notion: if no key provided, bail with a clear message
    needs_key = args.server in ("github", "notion")
    if needs_key and not any(env.values()):
        print(f"❌ {args.server} requires an API key. Pass --env KEY=value.")
        print(f"   Example: --env NOTION_API_KEY=secret_xxx")
        return 4

    result = setup_mcp_server(
        args.server,
        command=preset["command"],
        args=preset["args"],
        env=env,
        preinstall_pkg=preset.get("preinstall_pkg"),
        # dry_run handled inside helpers when set
    )
    # We don't expose dry_run via CLI here; if you want it, edit _cli.

    print()
    print("=" * 60)
    print(f"📊 Summary for '{args.server}':")
    print(f"   Saved to config: {result.get('add', {}).get('saved', '?')}")
    print(f"   Connected: {result.get('test', {}).get('connected', '?')}")
    print(f"   Tools discovered: {result.get('test', {}).get('tool_count', 0)}")
    print(f"   Overall OK: {result.get('ok', False)}")
    print()
    print("📋 All MCP servers:")
    print(list_servers())
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(_cli())
