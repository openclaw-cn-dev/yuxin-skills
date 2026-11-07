# `hermes -p NAME` vs `hermes gateway run -p NAME`

**These look almost identical but do completely different things.**

| Command | What it does | What happens |
|---|---|---|
| `hermes -p agent-sales` | Starts a **CLI chat session** using the profile | Drops you into an interactive REPL. If the profile has no API key, prints `It looks like Hermes isn't configured yet` and asks `Run setup now? [Y/n]`. Profile's gateway is **NOT** started. |
| `hermes chat -p agent-sales` | Same as above | Same. |
| `hermes gateway run -p agent-sales` | Starts the **gateway daemon** for the profile | Connects to the Feishu wss, shows `Hermes Gateway Starting...`, prints `[Lark] connected to wss://...`. The bot is now live and will receive messages. |

**Symptom that you've got the wrong one:** the user reports "the bot doesn't reply". You check `hermes gateway list` and see `✗ agent-sales — not running` (but you thought you started it). Look at the terminal command you used — if it's `hermes -p` or `hermes chat -p`, the gateway never started.

**Symptom in logs:** if you DID start with `hermes -p NAME` and the profile has no API key, you'll see in the captured stdout:
```
It looks like Hermes isn't configured yet -- no API keys or providers found.
  Run:  hermes setup
Run setup now? [Y/n]
```
The process eventually times out and exits with code 0 — but `hermes gateway list` will still show that profile as `not running`.

**Fix:**
1. `hermes gateway stop --all` (clean up any old PIDs)
2. `hermes gateway run -p <name> 2>&1 | tee ~/hermes-gateway-logs/<name>.log` (start the actual gateway)
3. Wait ~10 seconds
4. `tail -15 ~/hermes-gateway-logs/<name>.log` — should see `connected to wss://msg-frontier.feishu.cn/...`

The bundled `hermes-agent` skill in this repo's `autonomous-ai-agents/hermes-agent/SKILL.md` lists the two commands in different sections but doesn't call out the trap explicitly. If you're onboarding Feishu agents, always use `hermes gateway run` for the daemon and `hermes chat` (or `hermes`) only for interactive testing of one profile at a time.
