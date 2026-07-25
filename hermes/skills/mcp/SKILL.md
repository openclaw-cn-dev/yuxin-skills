---
name: mcp
description: Model Context Protocol — connect MCP servers to Hermes for tool discovery and integration. Load when you need to configure, register, or work with MCP servers.
version: 1.0.0
metadata:
  hermes:
    tags: [mcp, model-context-protocol, tools, integrations, agent]
---

# MCP — Model Context Protocol

Class-level umbrella for working with MCP (Model Context Protocol) servers and the built-in native MCP client.

## Children

- `native-mcp/` — MCP client: connect servers, register tools (stdio / HTTP transport).
- `mcp-builder/` — Guide for authoring high-quality MCP servers (Python FastMCP / Node SDK).

## Session-specific recipes (references/)

- `references/lookforge-chromadb-integration.md` — LookForge + ChromaDB + Hermes MCP integration: venv Python path issue, ChromaDB 0.6.x vs Docker 0.4.22, `PersistentClient` to bypass HTTP conflicts, direct `config.yaml` edit to avoid interactive `hermes mcp add`.
