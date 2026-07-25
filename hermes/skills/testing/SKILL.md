---
name: testing
description: Testing workflow skills for the Hermes ecosystem. Session-specific test recovery recipes live under `software-development/references/hermes-runtime/` instead — load this umbrella only when looking for test infrastructure patterns.
version: 1.0.0
metadata:
  hermes:
    tags: [testing, hermes, e2e]
---

# Testing

Class-level umbrella for testing patterns relevant to Hermes Agent.

## Children

- `dogfood/` — Systematic exploratory QA of web apps via the browser toolset: find bugs, capture evidence, produce a structured report.

## Related

- `software-development/references/hermes-runtime/e2e-test-recovery.md` — Manual e2e test recovery when subagents time out.
- `software-development/test-driven-development/` — RED-GREEN-REFACTOR methodology.
