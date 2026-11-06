# Lead Intake & Registration (客户登记)

## Where leads come from

| Source | How they arrive | First step |
|---|---|---|
| Click-to-message ads (WhatsApp, Messenger, Instagram) | Chat opens with a prefilled message | Instant greeting + one qualifying question |
| Website form / quote form | Form submission | Auto-confirmation email + reply in chat or email within the hour |
| Website chat widget | Live chat | Answer, then ask for email or WhatsApp to continue |
| Creator links / codes | DM or site visit | Tag the creator source |
| Cold email replies | Email thread | Move serious buyers to a call or WhatsApp if they prefer |
| Trade shows / events | Business card, QR code | Register the same day with event tag |

## Intake form fields

Keep forms short. Every extra field lowers completion; ask the rest in chat.

**B2C (3–4 fields)**
- First name
- Email or WhatsApp number (with country code)
- What are you looking for? (dropdown of main use cases)
- Consent checkbox: "I agree to receive messages about my inquiry and offers. Unsubscribe anytime."

**B2B quote form (5–7 fields)**
- Name, company, work email
- Country
- Product interest (dropdown)
- Estimated quantity (ranges: <300, 300–1,000, 1,000–5,000, 5,000+)
- Timeline (ranges: this month, 1–3 months, later, just researching)
- Notes (optional)
- Consent checkbox

## Registration sheet (simple CRM)

One row per lead. A spreadsheet works until roughly a few hundred active leads; then move to a CRM.

| Column | Example |
|---|---|
| Lead ID | L-0142 |
| Date in | 2026-11-02 |
| Name | Megan R. |
| Company (B2B) | Blue Ridge Gifts |
| Country / time zone | US / Eastern |
| Channel | WhatsApp |
| Contact | +1 … / email |
| Source | Meta ad C017 / creator_amy / cold email seq A |
| Interest | 20 oz tumblers, custom logo |
| Quantity / budget | 300–1,000 units |
| Timeline | 1–3 months |
| Score | 8 (see `lead-qualification.md`) |
| Stage | New → Contacted → Qualified → Quote/Offer sent → Won / Lost / Nurture |
| Owner | Aron |
| Last contact | 2026-11-03 |
| Next step + date | Send samples 11-05 |
| Lost reason | (price / timing / no reply / bought elsewhere) |
| Consent | Yes, form 11-02 |

## Tags

Use a small fixed set so filtering stays useful:
- Source: `ad`, `creator`, `cold-email`, `organic`, `event`, `referral`
- Temperature: `hot`, `warm`, `cold`
- Type: `retail-buyer`, `distributor`, `brand`, `end-customer`
- Issue: `price-objection`, `shipping-question`, `needs-sample`

## Auto-replies

**Instant greeting (click-to-chat ad)**
> Hi! Thanks for reaching out to CoreSeat 👋 Quick question so I can help faster: is this for your office chair, your car, or both?

**Outside business hours**
> Thanks for your message! We're offline right now (we reply 9 am–6 pm ET). We'll get back to you first thing. In the meantime, our FAQ covers shipping and returns: [link]

**B2B quote form confirmation (email)**
> Hi {name}, thanks for your inquiry about {product}. I'll send pricing and lead times within one business day. To make the quote accurate: which colors and quantities are you considering? — Lily, Brightwell Drinkware

## Consent and privacy

- Only message people who contacted you or opted in. Record when and how they consented.
- Honor "stop" or unsubscribe requests immediately and mark them in the sheet.
- WhatsApp Business has rules on templates and messaging outside the customer-service window; EU/UK contacts fall under GDPR. Confirm current platform and legal requirements.
- Don't store payment card details or ID documents in the sheet or chat exports.
