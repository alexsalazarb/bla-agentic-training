# Product Context — syncro-flutter

> Who uses this and what it does for them. Changes when product direction shifts.

**Memory tier**: Semantic.
**Update cadence**: When a feature area is added/retired or the target user changes.
**Last updated**: 2026-09-23

## Who

Field-service IT technicians using the Syncro MSP platform on a phone while on-site or on the move. Secondary: end users/customers interacting with a technician's work (e.g. signing off on forms).

## What the product does for them

| Area | What it covers |
|------|-----------------|
| Tickets | View, update, and manage support tickets; worksheets, timer entries, charges |
| Assets | Browse and filter customer assets (by type, saved search, customer) |
| Real-time chat | WebSocket-based chat tied to tickets/customers |
| Appointments | Create/update appointments, including location type and auto-filled location |
| Time tracking | Clock in/out, time-clock state synced with push notifications |
| Push notifications | Deep-link routing from FCM notifications into the relevant screen |
| Authentication | OAuth2 login, including passkey sign-in |

## Representative user stories

- As a technician, I want to see a customer's assets filtered by type or saved search, so I can find the right device quickly on-site.
- As a technician, I want to chat in real time about a ticket, so I don't have to switch to another app to coordinate.
- As a technician, I want my time clock state to stay accurate even if I edited a historical entry on the web, so my hours are correct.
- As a technician, I want to capture a customer's signature on an intake/outtake form directly in the app, matching what I'd do on the web, so paperwork doesn't require a separate device.
- As a technician, I want push notifications to take me straight to the relevant ticket or chat, not just open the app.

## In-flight product initiative (see `active_context.md` for status)

Mobile Intake/Outtake Form support: let a technician view a ticket's intake/outtake form as a live-rendered PDF (matching the web flow exactly, since it's the same render path) and capture a signature on it, reusing the existing ticket-update endpoint. This is scoped to reach parity with an existing web feature, not to introduce new product behavior.

## Explicitly deferred product behavior

- Passkey **discoverable** login (usernameless flow) — deferred: blocked on a subdomain-resolution gate and unclear scope for which relying-party ID to use. Edge case, not currently tracked as a ticket.
- Mobile self-enforcing "must complete outtake form before resolving a ticket" (full web parity) — open product question, not yet decided.
