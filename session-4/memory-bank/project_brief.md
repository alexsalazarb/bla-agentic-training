# Project Brief — syncro-flutter

> Why this project exists and what it's bounded by. Rarely changes.

**Memory tier**: Semantic — stable facts only.
**Update cadence**: Rarely (only on real scope changes, e.g. a new platform target or a pivot in product direction).
**Last updated**: 2026-09-23

## What

Syncro MSP mobile app — a field-service platform for IT technicians. Covers tickets, assets, real-time chat, appointments, and time tracking, on iOS and Android.

## Goals

- Give field technicians a mobile-first way to manage their day: view/update tickets, log time, chat with dispatch/customers, manage assets, and handle appointments — without needing the desktop web app.
- Keep mobile at close feature parity with the existing web app for technician-facing workflows (e.g. ticket intake/outtake forms, asset filtering) rather than diverging.
- Ship reliably to the App Store and Google Play on a recurring release cadence.

## Scope

**In scope**: technician-facing mobile workflows — ticket lifecycle, asset browsing/filtering, chat, appointments, time clock, push notifications, authentication (including passkeys).

**Out of scope for the mobile app**: admin/back-office functionality, POS/checkout flows (web-only), anything requiring the full desktop web feature set.

## Constraints

- Single codebase for iOS + Android (Flutter/Dart).
- Production release trains gated through app store review — release cadence is not instantaneous.
- Mobile consumes a shared backend API also used by the web app; new backend surface area (e.g. new endpoints/fields) is a cross-team dependency, not something mobile controls unilaterally.
- OAuth2-based auth; full automatic token refresh has known edge cases (see `tech_context.md`).

## Non-Goals

- Not a replacement for the web app's full admin capabilities.
- Not pursuing a separate design system from the web product — mobile follows product/UX parity with web where practical.

## Open Questions

- None at the project-brief level currently tracked — see `active_context.md` for in-flight open decisions on specific initiatives.
