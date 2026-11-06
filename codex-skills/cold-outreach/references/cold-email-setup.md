
# Cold Email Setup (Cold Start)

## Goal

A sending setup that protects the main domain, lands in the inbox, and can grow volume safely, while staying within anti-spam law.

## Before you start: gather context

- Main company domain and website
- Target: B2B buyers, distributors, retailers, partners, agencies
- Planned daily volume and sending tool
- Whether any domain has been used for cold email before (and its reputation)

## Infrastructure

1. **Separate sending domains.** Do not send cold email from the main company domain. Register 1–3 secondary domains that clearly relate to the brand (for example getbrand.com, brandhq.com) and redirect them to the main website.
2. **Mailboxes.** A few real-named mailboxes per domain on a reputable provider. Set a profile photo and a proper signature.
3. **Authentication** on every sending domain:
   - SPF: authorizes the mail provider
   - DKIM: signs messages
   - DMARC: start with a monitoring policy, tighten later
4. **Custom tracking domain** if the tool tracks links; better still, keep first emails link-free and turn off open tracking for best deliverability.

## Warm-up and ramp

- Warm up new mailboxes for roughly 2–4 weeks before real campaigns.
- Start real sending low and increase gradually; keep per-mailbox volume modest (dozens per day, not hundreds). Scale by adding mailboxes and domains, not by pushing one mailbox harder.
- Spread sends through the recipient's business hours (US time zones for US prospects).

## List hygiene

- Build lists from relevant, business-role contacts only.
- Verify every address before sending; keep bounce rate under about 2%.
- Remove anyone who asks to stop, immediately and across all mailboxes.

## Compliance

- **CAN-SPAM (US)**: no misleading From names or subject lines, include a valid physical postal address, provide a clear way to opt out, and honor opt-outs within 10 business days.
- **Gmail and Yahoo sender requirements**: authenticate domains, keep spam complaint rates very low (well under 0.3%), and, for bulk senders, support one-click unsubscribe.
- **Other markets**: EU/UK (GDPR, PECR) and Canada (CASL) have stricter consent rules; check before emailing contacts there.
- These rules change; tell the user to confirm current requirements.

## Health monitoring

Track weekly per mailbox: bounce rate, spam complaints, reply rate, and inbox placement tests. If bounce or complaints rise, pause that mailbox, clean the list and review copy.

## Common mistakes for sellers new to overseas outreach

- Sending from the main domain and damaging its reputation for normal business email
- Buying unverified lists and blasting thousands on day one
- HTML-heavy emails with images, attachments and many links in the first touch
- No unsubscribe line and no postal address

## Output format

1. Infrastructure checklist with status
2. DNS records to add (SPF, DKIM, DMARC) explained in plain language
3. Four-week warm-up and ramp schedule
4. Weekly health dashboard metrics and thresholds
5. Hand-off to `references/cold-outreach-copy.md` for the emails themselves
