# Feishu Re-pairing Notes

This note captures the practical sequence that worked when the user reissued Feishu credentials for an existing Hermes profile.

## Working sequence

1. Confirm where credentials are actually stored:
   - `~/.hermes/profiles/<profile>/.env` may override the default `~/.hermes/.env`.
   - Check both before editing.

2. Update the active profile env with the new Feishu values:
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`
   - Keep existing `FEISHU_DOMAIN=feishu` and `FEISHU_CONNECTION_MODE=websocket` unless the user says otherwise.

3. Restart the gateway with replacement semantics:
   - `hermes gateway run --replace -p <profile>`
   - This avoids the old PID lock blocking the refreshed instance.

4. Validate by watching the gateway log for a websocket connection line:
   - Look for `connected to wss://...`
   - A running gateway alone is not enough; confirm the new credentials actually connected.

## Notes

- If the profile gateway is already running, `hermes gateway run -p <profile>` will usually fail with an existing PID message.
- A successful websocket connection is the fastest smoke test before doing a human chat test in Feishu.
- The default profile `.env` and a profile-scoped `.env` can diverge; always update the one that is actually loaded by the profile you are restarting.
