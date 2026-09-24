# Progress — syncro-flutter

> Status snapshot: done / in progress / next / known issues.

**Memory tier**: Semantic (status facts), sourced from episodic history.
**Update cadence**: At session end; supersedes prior entries rather than accumulating narrative.
**Last updated**: 2026-09-23

## Done (recent, representative — not exhaustive)

- Firebase Performance Monitoring integrated (HTTP latency, screen traces, app-init/ticket-load custom traces).
- Passkey admin-fallback sign-in fix — shipped and verified on a QA build, iOS + Android.
- Fixed a session "zombie" bug: a refresh-token deadlock could leave the app looking logged-in with every screen empty; resolved by isolating the token-refresh HTTP call from the shared retry interceptor and forcing logout on a genuine refresh rejection.
- Asset Index: added Customer filter with paginated, server-side-sorted picker; added a "Tickets"/"Assets" cross-navigation button on Customer Detail.
- Fixed asset/customer/ticket detail navigation so pressing Back from a detail screen preserves an open search's query and results.
- Fixed 11 production Crashlytics issues across 9 root causes (iOS + Android) in one remediation pass; 1 issue closed as permanently blocked due to lack of symbolication tooling.
- Flutter upgraded 3.32.4 → 3.44.1 (full execution plan, 10/10 tasks).
- Expanded Patrol integration test coverage from ~14% to ~70% of screens (two phases).
- Fixed iOS chat list flicker and wrong sort order (duplicate WebSocket listener race condition).
- Fixed stuck ticket timer caused by stale `SharedPreferences` surviving Android Auto-Backup.
- Pendo SDK upgraded for Android Play Store consent/tracking compliance.

## In progress

- **Intake/outtake form signature capture** — blocked on a backend token-minting endpoint; domain-model and widget-level mobile work can proceed independently.
- **Android R8/ProGuard re-enable** — local investigation and rule fixes done; blocked on manual Play Store internal-testing validation (human step) before the release-process integration task.

## Next (not started, queued)

- Search delegate pagination: bring infinite-scroll + pull-to-refresh to asset search, following the existing `AssetsView` pagination pattern.
- Standardize domain-model serialization: migrate all models from mixed `fromMap`/`fromJson`/`toMap`/`toJson` naming to a single `fromJson`/`toJson` convention; pure technical cleanup.

## Known issues (open, not yet scheduled)

- No localization support despite hardcoded-string markers implying future intent — all user-facing strings are hardcoded.
- A few cubits take sibling cubits as constructor dependencies, creating implicit DI-registration-order requirements that fail silently if violated.
- Some navigation sequencing relies on fixed-duration delays rather than being event-driven — fragile under slow-device conditions.
- Use cases live under each feature's `infrastructure/` layer rather than `domain/` — a known, accepted deviation from strict Clean Architecture; new code follows the existing convention rather than fixing it piecemeal.
- One directory name contains a space, requiring a URL-encoded import path — flagged for a future rename, not yet done.

## Open question (product, unscheduled)

- Passkey discoverable (usernameless) login is deferred, blocked on a subdomain-resolution gate and unresolved relying-party-ID scope; no ticket filed yet.
