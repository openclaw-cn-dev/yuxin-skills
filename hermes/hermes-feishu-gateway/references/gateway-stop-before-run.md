# Why You Must `hermes gateway stop --all` Before `run`

Hermes tracks gateway processes in a PID file (typically `~/.hermes/gateway.pids` or per-profile). When you `hermes gateway run -p <name>` and an old gateway is still registered, the new process exits immediately with:

```
Gateway already running (PID 41256).
   Use 'hermes gateway restart' to replace it,
   or 'hermes gateway stop' to kill it first.
   Or use 'hermes gateway run --replace' to auto-replace.
```

**But here's the trap:** in our 4-agent onboarding session, the FIRST batch of `hermes -p` (chat mode) processes timed out and exited, but the PID file still showed them as `running`. So the second batch of `hermes gateway run` was rejected with the "already running" error — and `hermes gateway list` showed a PID that didn't exist anymore.

**Solution:** always do `hermes gateway stop --all` before the first `run` of a session:
```
hermes gateway stop --all 2>&1
hermes gateway list  # verify all show not running
hermes gateway run -p <name> 2>&1 | tee <log>   # for each profile
```

**`--replace` is risky** in this scenario: it silently kills the registered PID and starts a new one, but the registered PID might be a stale entry for a process that already exited. `--replace` then tries to kill nothing, succeeds, and starts the new gateway — works, but the error path is murky. Stop-then-run is more debuggable.

**After startup, verify:**
- `hermes gateway list` shows your profiles as `running` with new PIDs
- `tail -15 <log>` shows the wss connection line
- The `No user allowlists configured` warning is NOT present (see `references/allowlist-default-deny.md`)
