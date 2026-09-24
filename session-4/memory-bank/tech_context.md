# Tech Context — syncro-flutter

> Stack, dev setup, architecture, conventions. Changes when the team adopts/replaces a tool or pattern.

**Memory tier**: Semantic.
**Update cadence**: When stack, architecture, or conventions change — not per-task.
**Last updated**: 2026-09-23

## Stack

| Aspect | Value |
|--------|-------|
| Platform | Flutter (iOS + Android) |
| Language | Dart 3.x (`>=3.8.0 <4.0.0`) |
| State management | `flutter_bloc` 9.x — Cubit-first |
| Navigation | `go_router` 14.x — `StatefulShellRoute.indexedStack` (5 bottom tabs) |
| DI | `get_it` 8.x (singletons) + `BlocProvider`/`RepositoryProvider` (widget-tree scoped) |
| HTTP | `dio` 5.x via a `NetworkService` abstraction |
| Local DB | `hive` 2.x + `shared_preferences` |
| Real-time | `phoenix_socket` — singleton WebSocket service for chat |
| Auth | OAuth2 (`oauth_webauth`) + `flutter_secure_storage`; passkeys supported |
| Error handling | `dartz` `Either<Failure, T>` throughout all layers |
| Testing | `flutter_test` + `mockito` + `bloc_test`; Patrol for integration tests |
| Version manager | `fvm` — always prefix Flutter commands with `fvm` |

## Branch model

- `develop` — integration branch; **branch all plans/features from here**, not `main`.
- `main` — vestigial (3 commits total, no Flutter source); `origin`'s default HEAD points here but nobody develops on it. Mistaking `main` for the integration branch is a recurring error (recurred 3x historically) — verify with `git log --oneline -3 main` vs `develop` if unsure.
- `master` — production branch; only touched at release time, fast-forwarded to a tagged release commit.

## Dev commands

```bash
fvm flutter run                          # run app
fvm flutter run --dart-define=FLAVOR=qa  # QA environment
fvm flutter build apk                    # Android build
fvm flutter build ipa                    # iOS build
fvm flutter test                         # unit + widget tests
fvm flutter test --coverage
fvm flutter pub run build_runner build --delete-conflicting-outputs  # regenerate mocks
fvm flutter analyze
fvm dart format .
```

## Architecture

Clean-Architecture-ish, per-feature layering under `lib/features/[feature]/`:

```
domain/         # Entities, params, repository interfaces, response types
infrastructure/ # RepositoryImpl + UseCases (use cases live here, not domain/ — known deviation)
application/    # Cubits (state management)
presentation/   # Pages, widgets
```

17 features: alerts, appointments, asset_detail, assets, authentication, chat, chat_detail, customers, dashboard, end_user, home, settings, splash, technicians, ticket, time_clock, unlock_app.

## Core conventions

- Use `safeEmit()`, never `emit()` directly, in cubits (`core/utils/cubit_extension.dart`).
- Use `logger()` from `core/utils/logger.dart`, never `print()`/`debugPrint()`.
- Repositories never throw — always return `Either<Failure, T>`.
- Feature widgets never call `NetworkService` directly — go through repository → use case → cubit.
- Don't register feature repositories in GetIt — use widget-tree `RepositoryProvider` instead (double-registration was a past bug, now resolved).
- No `BuildContext` use after an `await` without checking `mounted`.
- `const` constructors wherever possible.
- Dispose all `AnimationController`/`StreamSubscription`/etc. in `dispose()`.
- Naming: `XCubit`, `XRepository`/`XRepositoryImpl`, `XUseCase`, `XParams`; files snake_case.
- No spaces in directory names (one existing violation is tracked as tech debt, not to be repeated).

## Known architectural debt (tracked, not urgent)

- Use cases live in `infrastructure/` instead of `domain/` — established (if non-canonical) project convention; new code should follow it rather than fix it ad hoc.
- No localization set up (`l10n/` absent) despite `.hardcoded` markers implying intent to localize later.
- A few cubits take other cubits as constructor dependencies, creating implicit DI-ordering requirements.
- Some navigation sequencing relies on fixed `Future.delayed` timings rather than event-driven sequencing.

## Auth / token refresh

Token refresh is implemented via a dedicated `AuthTokenClient` isolated from the main Dio retry interceptor (fixed after a prior deadlock bug — see `progress.md` "known issues"). Do not assume refresh is a stub; it's real, but isolate any changes to it from the shared network client to avoid reintroducing the deadlock class of bug.

## CI/Release

- Releases are tagged `{version}+{build}` and `master` is fast-forwarded to that commit.
- Android build currently ships with R8/ProGuard minification **disabled** (`minifyEnabled false`) due to a history of Play Store–only crashes; re-enabling it is an active initiative (see `active_context.md`).
