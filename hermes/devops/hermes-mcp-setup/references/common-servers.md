# Common MCP Servers — Quick Reference (Windows)

The 10 most-requested MCP servers. Each row = install command, args template,
required env vars, expected tool count, and the one specific gotcha for that
server. Verified on 2026-06-13.

| Server | Install | Args template | Env vars | Tools | Gotcha |
|---|---|---|---|---|---|
| **fetch** | `uvx mcp-server-fetch` | (none, just command) | none | 3 | Already installed by default in Hermes |
| **filesystem** | `npm install -g @modelcontextprotocol/server-filesystem` | `-y '@modelcontextprotocol/server-filesystem' 'C:/path1' 'C:/path2'` | none | 14 | Paths must be absolute; backslashes need `/` not `\` |
| **notion** | `uvx --from notion-mcp-server notion-mcp.exe` | `--from 'notion-mcp-server' 'notion-mcp.exe'` | `NOTION_API_KEY` | ~20 | Create internal integration at https://www.notion.so/my-integrations first |
| **github** | `npm install -g @modelcontextprotocol/server-github` | `-y '@modelcontextprotocol/server-github'` | `GITHUB_PERSONAL_ACCESS_TOKEN` | ~26 | Token needs `repo` + `read:user` scopes; classic token only (not fine-grained) |
| **slack** | `npm install -g @modelcontextprotocol/server-slack` | `-y '@modelcontextprotocol/server-slack'` | `SLACK_BOT_TOKEN` + `SLACK_TEAM_ID` | ~15 | Bot must be invited to channels before tools can read them |
| **linear** | `npx -y mcp-server-linear` | (none) | `LINEAR_API_KEY` | ~12 | API key at https://linear.app/settings/api |
| **airtable** | `npx -y airtable-mcp-server` | (none) | `AIRTABLE_API_KEY` | ~5 | Personal access token at https://airtable.com/create/tokens |
| **sentry** | `npx -y @modelcontextprotocol/server-sentry` | (none) | `SENTRY_AUTH_TOKEN` | ~7 | Auth token at https://sentry.io/settings/account/api/auth-tokens/ |
| **brave-search** | `npx -y @modelcontextprotocol/server-brave-search` | (none) | `BRAVE_API_KEY` | 2 | Free tier = 1 query/sec, 2000 queries/month |
| **google-drive** | `npx -y @modelcontextprotocol/server-gdrive` | (none) | `GDRIVE_OAUTH_CREDENTIALS` (JSON path) | ~10 | OAuth flow needed; credentials file path is the env var, not the key |

## Universal install recipe (Windows)

```python
import subprocess
from pathlib import Path

# 1. Find npm
npm = Path(r"C:\Program Files\nodejs\npm.cmd")
assert npm.exists()

# 2. Pre-install to avoid npx 0xb0 UTF-8 error
subprocess.run([str(npm), "install", "-g", "@modelcontextprotocol/server-<name>"], timeout=120)

# 3. Add MCP server with y/N stdin feed
args_list = [
    "hermes", "mcp", "add", "<name>",
    "--command", "npx",
    "--args", "-y",
    "--args", f"'@modelcontextprotocol/server-<name>'",
]
if env_vars:
    args_list += ["--env", f"<KEY>=<value>"]

subprocess.run(args_list, input="y\n", capture_output=True, text=True, timeout=60)

# 4. Test
subprocess.run(["hermes", "mcp", "test", "<name>"], timeout=30)
```

## Server discovery

For the full list of official/community MCP servers:
- https://github.com/modelcontextprotocol/servers (official)
- https://mcp.so/ (community catalog)
- https://glama.ai/mcp/servers (curated)
