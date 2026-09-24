# Active Context — syncro-flutter

> What's in flight right now. EPISODIC — short-lived by design.

**Memory tier**: Episodic.
**Update cadence**: At session end, not during coding. Prune finished/stale items — do not let this become an archive; completed work moves to `progress.md`.
**Last updated**: 2026-09-23

## Currently active plans

| Plan | State | Blocker |
|------|-------|---------|
| Intake/outtake form support (signature capture) | Blocked | Waiting on a backend endpoint to mint a PDF-preview token; mobile side (fields, params, signature widget) can proceed, but the screens can't integrate until it lands |
| Android R8/minification re-enable | Blocked | Task 3 (manual Play Store internal-testing validation) requires a human to run and confirm no crashes before continuing to the release-integration step |
| Search delegate pagination (infinite scroll for asset search) | Not started | None — next up when picked up |
| Standardize model serialization (`fromMap`/`toMap` → `fromJson`/`toJson`) | Not started | None — technical cleanup, no user-facing urgency |

## Recent decisions (last ~1-2 weeks)

- **Intake/outtake forms — architecture pivot**: dropped the original "poll ticket attachments for a generated PDF" design in favor of embedding a live-rendered PDF URL (same content, no async wait, no stale-attachment race). The old design is kept, not deleted, as a documented fallback in case the backend dependency stalls indefinitely.
- **Intake/outtake forms — signature validation**: confirmed (by testing the web app directly) that web accepts any non-empty mark as a valid signature, with no minimum-stroke heuristic. Mobile will match that bar exactly rather than being stricter.
- **Firebase Performance Monitoring**: integrated and merged to `develop`; one planned trace (chat-socket-connect) was deliberately dropped from scope during implementation rather than blocking the merge on it.

## Open questions blocking a specific plan (not general backlog)

- Intake/outtake forms: should resolving a ticket from mobile require completing the outtake form first, matching web? Not yet decided by product.
- Intake/outtake forms: is it acceptable that mobile won't show the *current* signature as a standalone image before re-signing (web does; the API doesn't expose that asset today)? Pending product sign-off.

## Recently resolved (context for next session, will be pruned once stale)

- A production Android passkey sign-in issue (wrong relying-party ID behavior) was escalated after confirming client-side config (asset links, RP ID, cert) was correct — resolution was outside the mobile codebase.
- Passkey admin-fallback bug fix shipped and verified end-to-end; discoverable (usernameless) passkey login remains explicitly deferred (see `product_context.md`).
