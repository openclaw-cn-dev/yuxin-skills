#!/usr/bin/env bash
# mcp-add-filesystem.sh — One-shot install + configure + test for the
# filesystem MCP server (the most common, zero-config server).
#
# Usage: bash mcp-add-filesystem.sh [path1] [path2] [...]
# Default paths: Desktop + Documents under the current user's home.

set -euo pipefail

# 1. Args
paths=("$@")
if [ ${#paths[@]} -eq 0 ]; then
    # Detect Windows-style home
    if [ -n "${USERPROFILE:-}" ]; then
        paths=(
            "$USERPROFILE/Desktop"
            "$USERPROFILE/Documents"
        )
    elif [ -n "${HOME:-}" ]; then
        paths=(
            "$HOME/Desktop"
            "$HOME/Documents"
        )
    else
        echo "ERROR: pass at least one path as argument" >&2
        exit 2
    fi
fi

echo "📁 Will grant filesystem MCP access to:"
for p in "${paths[@]}"; do
    echo "  - $p"
done
echo

# 2. Find npm
npm=""
for candidate in \
    "/c/Program Files/nodejs/npm.cmd" \
    "/c/Program Files (x86)/nodejs/npm.cmd" \
    "C:/Program Files/nodejs/npm.cmd"; do
    if [ -f "$candidate" ]; then
        npm="$candidate"
        break
    fi
done

if [ -z "$npm" ]; then
    echo "❌ npm not found. Install Node.js first." >&2
    exit 3
fi
echo "✅ npm at: $npm"

# 3. Pre-install package globally to avoid npx 0xb0 UTF-8 error
echo "📦 Installing @modelcontextprotocol/server-filesystem globally..."
"$npm" install -g @modelcontextprotocol/server-filesystem

# 4. Remove any existing filesystem server (clean slate)
hermes mcp remove filesystem 2>/dev/null || true

# 5. Build the hermes mcp add command
args=(hermes mcp add filesystem --command npx --args -y
      --args '@modelcontextprotocol/server-filesystem')
for p in "${paths[@]}"; do
    args+=(--args "$p")
done

echo "🔌 Adding filesystem MCP server..."
echo "  cmd: ${args[*]}"
echo

# 6. Run with stdin "y" for the interactive y/N prompt (only if needed)
"${args[@]}" <<< "y" || true

# 7. Verify
echo
echo "🧪 Testing connection..."
hermes mcp test filesystem

echo
echo "📋 Final state:"
hermes mcp list

echo
echo "✅ Done. The filesystem MCP server is now installed and enabled."
echo "   Available tools: read_file, write_file, list_directory, search_files,"
echo "   edit_file, move_file, create_directory, get_file_info, etc. (14 total)"
