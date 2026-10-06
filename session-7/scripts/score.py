#!/usr/bin/env python3
"""V-Score aggregator: the deterministic half of the system.

Scorer agents reason; this script only validates, weights, sums, maps to a
verdict and keeps the memory bank. The LLM never does arithmetic.

Usage:
  score.py aggregate [--save]   # stdin: {"idea": str, "scores": {criterion: {score, reason}}}
  score.py recall "<idea>"      # most similar past run from the memory bank
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "memory" / "scores.json"
THRESHOLD = 65
BORDERLINE_MARGIN = 5  # |axis - THRESHOLD| <= margin → a ±1 scorer swing could flip the verdict

CRITERIA = {
    # key: (axis, weight, label)
    "novelty":   ("poc", 3, "Technical Novelty"),
    "scope":     ("poc", 4, "Defined Scope"),
    "resources": ("poc", 2, "Resource Accessibility"),
    "outcome":   ("poc", 1, "Measurable Outcome"),
    "pain":      ("market", 4, "Pain Severity"),
    "pay":       ("market", 3, "Willingness to Pay"),
    "size":      ("market", 2, "Market Size"),
    "moat":      ("market", 1, "Differentiation"),
}

VERDICTS = {
    (True, True):   ("go", "🚀 Go / Full Speed Ahead", "Excellent on both axes."),
    (False, True):  ("derisk", "🧪 De-risk First", "Strong demand, hard build. Spike the tech."),
    (True, False):  ("validate", "🔍 Validate Demand", "Buildable — but prove someone wants it."),
    (False, False): ("shelve", "🛑 Reframe or Shelve", "High risk on both axes."),
}


def _validate_entry(key: str, entry: dict) -> None:
    value = entry.get("score")
    if type(value) is not int or not 1 <= value <= 10:
        raise ValueError(f"{key}: score must be an integer 1-10, got {value!r}")
    if not str(entry.get("reason", "")).strip():
        raise ValueError(f"{key}: reason is required — never a number without a reason")


def _resolve(key: str, entry: dict) -> dict:
    """One scorer → as-is. Several blind samples → median score, reason from the median sample."""
    if "samples" not in entry:
        _validate_entry(key, entry)
        return entry
    samples = entry["samples"]
    if not samples:
        raise ValueError(f"{key}: samples must not be empty")
    for s in samples:
        _validate_entry(key, s)
    values = [s["score"] for s in samples]
    median = sorted(values)[(len(values) - 1) // 2]  # lower median keeps it an integer
    chosen = next(s for s in samples if s["score"] == median)
    return {"score": median, "reason": chosen["reason"], "samples": values, "spread": max(values) - min(values)}


def validate(scores: dict) -> dict:
    resolved = {}
    for key in CRITERIA:
        if key not in scores:
            raise ValueError(f"missing criterion: {key}")
        resolved[key] = _resolve(key, scores[key])
    return resolved


def aggregate(scores: dict) -> dict:
    scores = validate(scores)
    totals = {"poc": 0, "market": 0}
    for key, (axis, weight, _) in CRITERIA.items():
        totals[axis] += scores[key]["score"] * weight
    high = (totals["poc"] >= THRESHOLD, totals["market"] >= THRESHOLD)
    key, label, meaning = VERDICTS[high]
    return {
        "poc": totals["poc"],
        "market": totals["market"],
        "verdict": {"key": key, "label": label, "meaning": meaning},
        "borderline": [a for a in ("poc", "market") if abs(totals[a] - THRESHOLD) <= BORDERLINE_MARGIN],
        "scores": {k: scores[k] for k in CRITERIA},
    }


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def save_run(idea: str, result: dict, bank: Path = BANK) -> None:
    runs = json.loads(bank.read_text()) if bank.exists() else []
    runs.append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "idea": idea, **result})
    bank.parent.mkdir(parents=True, exist_ok=True)
    bank.write_text(json.dumps(runs, indent=2, ensure_ascii=False) + "\n")


def recall(idea: str, bank: Path = BANK) -> dict | None:
    if not bank.exists():
        return None
    query = _tokens(idea)
    best, best_sim = None, 0.0
    for run in json.loads(bank.read_text()):
        other = _tokens(run["idea"])
        sim = len(query & other) / len(query | other) if query | other else 0.0
        if sim > best_sim:
            best, best_sim = run, sim
    return best and {**best, "similarity": round(best_sim, 2)}


def report(idea: str, r: dict) -> str:
    lines = [f"## V-Score — {idea}", ""]
    for axis, title in (("poc", "PoC Viability"), ("market", "Market Viability")):
        lines += [f"### {title}: {r[axis]}/100", "", "| Criterion | Score | × | Reason |", "|---|---|---|---|"]
        for key, (ax, weight, label) in CRITERIA.items():
            if ax == axis:
                s = r["scores"][key]
                shown = f"{s['score']} ({'·'.join(map(str, s['samples']))})" if "samples" in s else s["score"]
                lines.append(f"| {label} | {shown} | {weight} | {s['reason']} |")
        lines.append("")
    v = r["verdict"]
    lines.append(f"### Verdict: {v['label']} — {v['meaning']}")
    if r["borderline"]:
        axes = " and ".join(f"{'PoC' if a == 'poc' else 'Market'} ({r[a]})" for a in r["borderline"])
        lines += ["", f"> ⚠️ Borderline: {axes} within ±{BORDERLINE_MARGIN} of {THRESHOLD}. "
                      "A one-point change in a heavy criterion could flip this verdict — treat it as low confidence."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    agg = sub.add_parser("aggregate")
    agg.add_argument("--save", action="store_true")
    rec = sub.add_parser("recall")
    rec.add_argument("idea")
    args = parser.parse_args()

    if args.cmd == "recall":
        hit = recall(args.idea)
        print(json.dumps(hit, indent=2, ensure_ascii=False) if hit else "No similar past idea.")
        return 0

    payload = json.load(sys.stdin)
    try:
        result = aggregate(payload["scores"])
    except ValueError as e:
        print(f"INVALID SCORER OUTPUT: {e}", file=sys.stderr)
        return 1
    if args.save:
        save_run(payload["idea"], result)
    print(report(payload["idea"], result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
