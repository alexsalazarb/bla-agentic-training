# Evidence — test run

Date: 2026-10-01. Private repo, isolated throwaway git worktree created from `develop`. One new test file (+112 lines), no production code changed. Per the rule for this training (the client repo keeps nothing extra), the worktree and its branch were **deleted after the run** — the raw logs below are the evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `fvm flutter test test/core/utils/string_helper_test.dart --reporter expanded` | `00:00 +18: All tests passed!` → raw log: [`flutter-test.log`](flutter-test.log) |
| Lint | `fvm flutter analyze test/core/utils/string_helper_test.dart` | `No issues found!` → raw log: [`flutter-analyze.log`](flutter-analyze.log) |
| Mutation | disable the `www.` guard in `isURLValid()`, re-run, restore | **2 of 18 fail**, exactly the 2 that target the guard → raw log: [`mutation-test.log`](mutation-test.log) |
| Scope | `git status -s` | only the new test file |
| Prior coverage | search for any test referencing the utils file | none (0 files) |

The raw logs are real tool output, trimmed only of the absolute local path and of `pub get` / plugin warnings (which list the private app's dependencies). The expanded reporter prints each test name, so the log maps 1:1 to the case table in the [session README](../README.md#the-tests).

## Do the tests protect anything? (mutation check)

A green run only proves the tests agree with the code today. To check they would catch a regression, the `www.` guard (the past backtracking fix) was switched off and the suite re-run:

- `isURLValid rejects www. host without a further label` → fails: `www.google` is accepted again.
- `extractUrl returns null when the stripped candidate is no longer valid` → fails: returns `'www.google'` instead of `null`, because `extractUrl()` re-validates with `isURLValid()`.
- The other 16 still pass — they never reach the guard.

One fix, guarded by two tests in two functions, and no unrelated test breaks. That is the signal the tests are focused, not just green.

## History

The first run (2026-09-29) was written and run by a sub-agent in a throwaway worktree; its summary was published without raw output. On 2026-10-01 the 18 tests were rewritten from the case table, re-run, and the raw logs plus the mutation check were added.

Test and source code are not published (private client repo).
