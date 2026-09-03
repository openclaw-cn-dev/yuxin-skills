# Intended use

This skill strips machine-readable provenance marks and hygiene problems from content **you own or are authorized to process**.

## Appropriate

- Privacy: drop tool / device / AI provenance from your own files before you share them
- Engineering hygiene: remove invisible Unicode that breaks diffs, search, or paste
- Research: learn how text and C2PA marks work across vendors
- Local unmarked copies of your own drafts where policy allows it

## Not appropriate

- Academic fraud, or hiding AI assistance where disclosure is required
- Circumventing lawful transparency or platform disclosure rules
- Claiming cleaned content is “human-written” for compliance theater

A removed mark does **not** mean the content was never AI-assisted. Use the toolkit honestly.

## Honesty in reports

Always separate:

1. **Verifiable** removals (Unicode counts, metadata actions)
2. **Best-effort** statistical rewrite (no gold undetection claim)
3. **Optional / out-of-scope** channels (optional external pixel removal via CtrlRegen; audio/video watermarks, **C2PA soft binding**, secret-key detectors, and training backdoors are out of scope)

Do not imply that a successful C2PA / metadata strip means “no AI provenance left.” Soft-bound and SynthID-class media signals can survive. Point users at vendor verify tools when they need residual checks (see README *Residual risk after a clean*).

## Responsible use and liability

This project helps people understand and remove AI provenance marks from content they own or are authorized to process. Privacy, engineering hygiene, and research — including evaluating watermark robustness — are in bounds. Users must follow local law and use the tools responsibly. Maintainers disclaim liability for misuse.
