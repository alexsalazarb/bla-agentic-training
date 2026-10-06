# V-Score — Sample Runs

> Real scorer outputs captured on 2026-10-06 (reasons lightly condensed), aggregated by `scripts/score.py`.
> Scorers ran as fresh sub-agents reading the current `.claude/agents/*-scorer.md` (with calibration examples) and the lesson in `memory/lessons.md`.
> This file is the **backup** for the live demo — the live run is `/vscore "<judges' idea>"`.

## Calibration exam — `/vscore-eval`

| Idea | Expected | Actual | PoC | Market | Borderline | Pass |
|---|---|---|---|---|---|---|
| A Slack bot that summarizes each team channel's … | go | validate | 85 | 63 | market | ❌ |
| Real-time translation earbuds that let two peopl… | derisk | derisk | 39 | 65 | market | ✅ fragile |
| AI for everything: a platform that uses AI to im… | shelve | shelve | 26 | 31 | — | ✅ |

**2/3 pass.** The Slack bot is the honest miss — see *Calibration story* below.

---

*Median of 3 blind samples per criterion (24 scorer runs).*

## V-Score — A Slack bot that summarizes each team channel's daily standup thread and posts a 5-bullet digest to the manager every evening.

### PoC Viability: 85/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Technical Novelty | 9 (9·9·9) | 3 | Slack API + LLM summarization + a cron trigger is commodity tech that has shipped many times. |
| Defined Scope | 8 (8·8·8) | 4 | One input (each channel's standup thread) → one output (5-bullet digest to the manager); fuzzy edges on thread detection and per-channel vs combined digests. |
| Resource Accessibility | 9 (9·9·9) | 2 | Slack Web/Events API and LLM APIs are public, cheap and documented; only workspace admin approval is a gate. |
| Measurable Outcome | 8 (8·8·8) | 1 | A digest visibly appears in the manager's DM each evening; digest quality needs light human review. |

### Market Viability: 63/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Pain Severity | 6 (6·6·6) | 4 | Managers reading many standup threads daily is a real recurring cost, but a time-and-visibility drain rather than hair-on-fire. |
| Willingness to Pay | 7 (7·7·7) | 3 | Clear buyer and teams already pay per seat for Slack standup tools (e.g. Geekbot); budget is team-level and Slack AI could bundle it. |
| Market Size | 8 (8·8·7) | 2 | Hundreds of thousands of Slack teams run standups with reachable managers; limited to async Slack standups. |
| Differentiation | 2 (2·2·2) | 1 | Thin LLM wrapper with no proprietary data or network effect; Slack AI recaps and Geekbot/Standuply already cover it. |

### Verdict: 🔍 Validate Demand — Buildable — but prove someone wants it.

> ⚠️ Borderline: Market (63) within ±5 of 65. A one-point change in a heavy criterion could flip this verdict — treat it as low confidence.

---

*Single blind sample per criterion (8 scorer runs).*

## V-Score — Real-time translation earbuds that let two people speaking different languages hold a natural face-to-face conversation.

### PoC Viability: 39/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Technical Novelty | 3 | 3 | Low-latency streaming ASR + translation + speech in a small wearable pushes the state of the art; no product ships it reliably. |
| Defined Scope | 4 | 4 | Bundles hardware, ASR, MT, TTS and a two-person flow; language pairs and latency targets undefined — needs a scoping decision first. |
| Resource Accessibility | 4 | 2 | Needs custom or tightly integrated earbud hardware; chaining speech APIs fast enough is hard for a small team. |
| Measurable Outcome | 6 | 1 | Latency and accuracy are measurable (WER, delay < ~2s), but a 'natural' conversation is subjective. |

### Market Viability: 65/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Pain Severity | 7 | 4 | People without a shared language face a real, recurring barrier and already hack workarounds with phone apps. |
| Willingness to Pay | 5 | 3 | Plausible traveler buyer, but no specific payer named; free translation apps make monetization unclear. |
| Market Size | 9 | 2 | Hundreds of millions of travelers, expats and international business users; earbuds are a mass-market channel. |
| Differentiation | 4 | 1 | Commodity speech models; Google, Apple and Timekettle ship or could add it; hardware + latency tuning give some edge. |

### Verdict: 🧪 De-risk First — Strong demand, hard build. Spike the tech.

> ⚠️ Borderline: Market (65) within ±5 of 65. A one-point change in a heavy criterion could flip this verdict — treat it as low confidence.

---

*Single blind sample per criterion (8 scorer runs).*

## V-Score — AI for everything: a platform that uses AI to improve any business process for any company.

### PoC Viability: 26/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Technical Novelty | 4 | 3 | No defined technical core; 'improve everything' is not a solved problem. |
| Defined Scope | 1 | 4 | Boundless: no single user, job or input-to-output boundary — no PoC can be cut from it. |
| Resource Accessibility | 4 | 2 | Names no specific data, APIs or integrations; needs depend on each customer's systems. |
| Measurable Outcome | 2 | 1 | Names no specific process or result, so success cannot be defined. |

### Market Viability: 31/100

| Criterion | Score | × | Reason |
|---|---|---|---|
| Pain Severity | 3 | 4 | Names no specific sufferer, process or cost. |
| Willingness to Pay | 3 | 3 | No buyer, budget line or paid alternative named. |
| Market Size | 4 | 2 | 'Any company' is an unbounded claim, not a reachable segment. |
| Differentiation | 2 | 1 | No proprietary data, integration or network effect; any AI vendor could replicate it. |

### Verdict: 🛑 Reframe or Shelve — High risk on both axes.

---

## Calibration story (how we got here)

| Step | Slack bot Market | Verdict | What we learned |
|---|---|---|---|
| 1. First run, no calibration | 53 | 🔍 | Pain scored 4 because competitors exist — moat's job leaking into pain |
| 2. `/vscore-learn` added a pain lesson | 50 | 🔍 | Lesson moved pain 4→5, but run-to-run noise (pay 7→5) swamped it |
| 3. Calibration examples (1 per quadrant, never the reference ideas) | 63 | 🔍 ⚠️ | Variance collapsed; Market jumped |
| 4. Median of 3 blind samples | 63 | 🔍 ⚠️ | 7/8 criteria unanimous → 63 is a **stable judgment**, not noise |
| 5. Richer wording ("EMs with 5+ teams, ~30 min/day") | 64 | 🔍 ⚠️ | Pain 6→7 but size 8→6: specificity trades pain for market size |

**Decision:** we did not tune the rubric until the Slack bot said Go — that would be overfitting.
The system says Validate Demand at 63–64, flags it ⚠️ Borderline, and shows the eight reasons why.
