# Session 6 — Designer & QA Workflows (QA track)

**Deliverable (2 of 2 this week): test generation workflow.** Pick a function, run the 5-step workflow, and arrive with 3+ tests you have read and understand.

- Result: **18 unit tests**, all passing, for two functions that had **zero** tests
- Evidence: [`evidence/test-run.md`](evidence/test-run.md)

> Context: real code from the Syncro MSP mobile app (Flutter), trainer-approved. The app code is private, so **no source or test code is published here**. This page describes the functions and the cases; the tests live on a branch in the private repo.

## The target

Two `String?` extensions from a shared utils file, used across the app (appointment locations, custom-field links, ticket creation):

| Function | What it does |
|---|---|
| `bool isURLValid()` | Regex URL validator, with a hand-written guard for `www.` hosts |
| `String? extractUrl()` | Finds the first `http(s)://` or `www.` URL in free text, strips trailing punctuation, re-validates with `isURLValid()` |

Why these: zero coverage, pure (no platform, no mocks), widely used, and the code carries a comment about a past regex **backtracking bug** fixed by the guard. A fix with no test is a regression waiting to happen.

## The 5 steps

| # | Step | What I did |
|---|---|---|
| 1 | Pick the function | Ranked 4 candidates by risk × ease with a read-only sub-agent. Ruled out 2 that were already well covered and 1 that needed a timezone singleton mocked |
| 2 | Read implementation | Read both functions and their 6 callers. Understood the `www.` guard *before* writing tests: without it, the regex treats `www.` as a label and `google` as the TLD, so `www.google` passes |
| 3 | Identify gaps | Null, empty, whitespace, `www.google` vs `www.google.com`, bare domain, no TLD, http/https, path+query+fragment; for extraction: no URL, multiple URLs, bare `www.`, trailing `.` and `)`, candidate that becomes invalid after stripping |
| 4 | Generate tests | 18 tests in 2 groups, matching the repo's test style (Arrange/Act/Assert). Expected values were checked against a throwaway probe script first, not guessed |
| 5 | Review & own | Ran them, ran the analyzer, read every test. Table below |

## The tests

| Group | Input | Expected |
|---|---|---|
| isURLValid | `null` · `''` | false |
| isURLValid | `'google .com'` (space inside) | false |
| isURLValid | `'google.com '` (trailing space) | false — see finding 1 |
| isURLValid | `'www.google'` | false — **locks in the backtracking fix** |
| isURLValid | `'www.google.com'` · `'google.com'` | true |
| isURLValid | `'google'` | false |
| isURLValid | `'http://google.com'` · `'https://google.com'` | true |
| isURLValid | `'https://google.com/path?q=1&lang=en#frag'` | true |
| extractUrl | `null` · `'Just call the office'` | null |
| extractUrl | `'Visit http://a.com or http://b.com'` | `'http://a.com'` (first wins) |
| extractUrl | `'See www.example.com for info'` | `'www.example.com'` |
| extractUrl | `'Visit http://google.com. Thanks'` | `'http://google.com'` |
| extractUrl | `'(http://google.com)'` | `'http://google.com'` |
| extractUrl | `'Contact www.google, ok'` | null — see finding 2 |

## Findings

1. **`isURLValid()` never trims.** `'google.com '` is rejected only because of the space check, although the URL is fine. Whether that is a bug depends on the callers: any that don't trim user input lose valid URLs. Asserted as *current behavior* with a comment, not "fixed" in the test. **Open question:** do all callers trim?
2. **`extractUrl()` can return `null` for realistic text.** `'www.google,'` → comma stripped → `'www.google'` → rejected by the guard. This is the guard doing its job, but it means a typo in a location field makes the link disappear silently.
3. `http://localhost:8080` is rejected (the regex needs a dotted host). By design for this app; noted, not tested.

No production code was changed. The rule from the session applies here too: when a test and the code disagree, **decide whether it is a bug or a wrong expectation — never just flip the assertion.** Both findings are documented in the test file as current behavior.

## Takeaways

1. Step 2 is the one that matters. Reading the guard's comment turned a generic "validate URLs" suite into a regression test for a real past bug.
2. Probing actual outputs before asserting stopped me from writing tests that encode guesses.
3. The most useful output of test generation was not the green run — it was the two questions it raised about callers.
