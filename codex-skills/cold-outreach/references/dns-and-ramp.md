# DNS Records & 4-Week Ramp

Fictional example: main domain `coreseat.com`; sending domains `getcoreseat.com` and `coreseathq.com`.

## DNS records (per sending domain)

Exact values come from the email provider; these show the shape.

| Type | Host | Value (example) | Purpose |
|---|---|---|---|
| TXT | @ | `v=spf1 include:_spf.provider.com ~all` | SPF: authorizes the provider to send |
| TXT / CNAME | `selector._domainkey` | Key provided by the mail provider | DKIM: signs messages |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@coreseat.com` | DMARC: start in monitor mode |
| CNAME | `track` | Provider's tracking host | Custom tracking domain (optional) |
| Redirect | @ | 301 → https://coreseat.com | Sending domain sends visitors to the real site |

Notes:
- Only one SPF record per domain; merge includes if you use several services.
- After 2–4 weeks of clean reports, move DMARC toward `p=quarantine`.
- Verify records with the provider's checker before warming up.

## Mailbox plan

| Domain | Mailboxes |
|---|---|
| getcoreseat.com | aron@, a.hou@ |
| coreseathq.com | aron@, partnerships@ (real person signature) |

Each mailbox: real name, photo, signature with company name, website and postal address.

## 4-week warm-up and ramp (per mailbox)

| Week | Warm-up tool | Real cold emails per day | Checks |
|---|---|---|---|
| 1 | On | 0 | Authentication passing, warm-up emails landing in inbox |
| 2 | On | 0–5 (only to highly relevant, verified contacts) | Bounce < 2%, no spam complaints |
| 3 | On | 10–20 | Reply rate tracked, inbox placement test |
| 4 | On | 20–30 | If healthy, add more mailboxes instead of more volume per mailbox |

Keep warm-up running at a low level while sending. Send during the recipient's business hours (US Eastern, Central, Pacific as appropriate).

## Weekly health thresholds

| Metric | Healthy | Action if worse |
|---|---|---|
| Bounce rate | < 2% | Pause, re-verify list |
| Spam complaints | Near zero (far below 0.3%) | Pause mailbox, review targeting and copy |
| Reply rate | Rising or stable | Rework personalization, offer, subject |
| Inbox placement test | Mostly inbox | Reduce volume, remove links/tracking, check DNS |

## Required footer (CAN-SPAM, US)

> Aron Hou · CoreSeat · [Real postal address]
> Not the right person or not interested? Just reply "no thanks" and I won't email again.

Honor every opt-out promptly and across all mailboxes. Rules change: confirm current requirements.
