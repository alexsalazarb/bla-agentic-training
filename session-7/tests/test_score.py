import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import score  # noqa: E402

CRITERIA = ["novelty", "scope", "resources", "outcome", "pain", "pay", "size", "moat"]


def scores(values: dict[str, int]) -> dict:
    return {k: {"score": v, "reason": f"reason for {k}"} for k, v in values.items()}


def uniform(n: int) -> dict:
    return scores({k: n for k in CRITERIA})


# PoC: 5*3 + 8*4 + 8*2 + 2*1 = 65 ; Market: 5*4 + 8*3 + 8*2 + 5*1 = 65
TIE_65 = {"novelty": 5, "scope": 8, "resources": 8, "outcome": 2,
          "pain": 5, "pay": 8, "size": 8, "moat": 5}


class TestAggregate(unittest.TestCase):
    def test_all_tens_is_100_100_go(self):
        r = score.aggregate(uniform(10))
        self.assertEqual((r["poc"], r["market"]), (100, 100))
        self.assertEqual(r["verdict"]["key"], "go")

    def test_all_ones_is_10_10_shelve(self):
        r = score.aggregate(uniform(1))
        self.assertEqual((r["poc"], r["market"]), (10, 10))
        self.assertEqual(r["verdict"]["key"], "shelve")

    def test_weights_applied_per_criterion(self):
        vals = {k: 1 for k in CRITERIA} | {"novelty": 2, "pain": 2}
        r = score.aggregate(scores(vals))
        self.assertEqual(r["poc"], 10 + 3)     # novelty weight 3
        self.assertEqual(r["market"], 10 + 4)  # pain weight 4

    def test_tie_at_exactly_65_is_high(self):
        r = score.aggregate(scores(TIE_65))
        self.assertEqual((r["poc"], r["market"]), (65, 65))
        self.assertEqual(r["verdict"]["key"], "go")

    def test_64_is_low(self):
        vals = TIE_65 | {"outcome": 1, "moat": 4}
        r = score.aggregate(scores(vals))
        self.assertEqual((r["poc"], r["market"]), (64, 64))
        self.assertEqual(r["verdict"]["key"], "shelve")

    def test_high_poc_low_market_is_validate_demand(self):
        r = score.aggregate(scores({"novelty": 10, "scope": 10, "resources": 10, "outcome": 10,
                                    "pain": 1, "pay": 1, "size": 1, "moat": 1}))
        self.assertEqual(r["verdict"]["key"], "validate")

    def test_low_poc_high_market_is_derisk(self):
        r = score.aggregate(scores({"novelty": 1, "scope": 1, "resources": 1, "outcome": 1,
                                    "pain": 10, "pay": 10, "size": 10, "moat": 10}))
        self.assertEqual(r["verdict"]["key"], "derisk")


class TestBorderline(unittest.TestCase):
    def test_axis_within_5_of_threshold_is_flagged(self):
        r = score.aggregate(scores(TIE_65))  # 65 / 65
        self.assertEqual(r["borderline"], ["poc", "market"])

    def test_edges_of_band_are_inclusive(self):
        # PoC 60: 5*3 + 7*4 + 8*2 + 1*1 ; Market 70: 6*4 + 8*3 + 8*2 + 6*1
        r = score.aggregate(scores({"novelty": 5, "scope": 7, "resources": 8, "outcome": 1,
                                    "pain": 6, "pay": 8, "size": 8, "moat": 6}))
        self.assertEqual((r["poc"], r["market"]), (60, 70))
        self.assertEqual(r["borderline"], ["poc", "market"])

    def test_outside_band_not_flagged(self):
        self.assertEqual(score.aggregate(uniform(10))["borderline"], [])
        self.assertEqual(score.aggregate(uniform(1))["borderline"], [])

    def test_report_warns_on_borderline(self):
        r = score.aggregate(scores(TIE_65))
        self.assertIn("⚠️ Borderline", score.report("x", r))

    def test_report_silent_when_clear(self):
        self.assertNotIn("Borderline", score.report("x", score.aggregate(uniform(10))))


def sampled(values: dict[str, list[int]]) -> dict:
    return {k: {"samples": [{"score": v, "reason": f"{k} says {v}"} for v in vs]}
            for k, vs in values.items()}


class TestMedianOfSamples(unittest.TestCase):
    def test_median_of_three_is_used(self):
        r = score.aggregate(sampled({k: [10, 10, 10] for k in CRITERIA} | {"pain": [6, 8, 7]}))
        self.assertEqual(r["scores"]["pain"]["score"], 7)
        self.assertEqual(r["market"], 100 - 3 * 4)

    def test_reason_comes_from_the_median_sample(self):
        r = score.aggregate(sampled({k: [5, 5, 5] for k in CRITERIA} | {"pay": [9, 4, 6]}))
        self.assertEqual(r["scores"]["pay"]["reason"], "pay says 6")

    def test_samples_and_spread_are_kept(self):
        r = score.aggregate(sampled({k: [5, 5, 5] for k in CRITERIA} | {"size": [3, 8, 5]}))
        self.assertEqual(r["scores"]["size"]["samples"], [3, 8, 5])
        self.assertEqual(r["scores"]["size"]["spread"], 5)

    def test_even_count_uses_lower_median_to_stay_integer(self):
        r = score.aggregate(sampled({k: [5, 5] for k in CRITERIA} | {"moat": [4, 7]}))
        self.assertEqual(r["scores"]["moat"]["score"], 4)

    def test_invalid_sample_rejected(self):
        with self.assertRaisesRegex(ValueError, "novelty"):
            score.aggregate(sampled({k: [5, 5, 5] for k in CRITERIA} | {"novelty": [5, 11, 5]}))

    def test_empty_samples_rejected(self):
        s = sampled({k: [5, 5, 5] for k in CRITERIA})
        s["scope"]["samples"] = []
        with self.assertRaisesRegex(ValueError, "scope"):
            score.aggregate(s)

    def test_report_shows_samples(self):
        r = score.aggregate(sampled({k: [5, 5, 5] for k in CRITERIA} | {"pain": [6, 8, 7]}))
        self.assertIn("7 (6·8·7)", score.report("x", r))


class TestValidation(unittest.TestCase):
    def test_missing_criterion_rejected(self):
        s = uniform(5)
        del s["moat"]
        with self.assertRaisesRegex(ValueError, "moat"):
            score.aggregate(s)

    def test_out_of_range_rejected(self):
        for bad in (0, 11):
            with self.assertRaises(ValueError):
                score.aggregate(scores({k: 5 for k in CRITERIA} | {"pay": bad}))

    def test_non_integer_rejected(self):
        s = uniform(5)
        s["size"]["score"] = 7.5
        with self.assertRaises(ValueError):
            score.aggregate(s)

    def test_empty_reason_rejected(self):
        s = uniform(5)
        s["scope"]["reason"] = "  "
        with self.assertRaisesRegex(ValueError, "reason"):
            score.aggregate(s)


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bank = Path(self.tmp.name) / "scores.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_appends_run(self):
        score.save_run("idea one", score.aggregate(uniform(5)), self.bank)
        score.save_run("idea two", score.aggregate(uniform(6)), self.bank)
        runs = json.loads(self.bank.read_text())
        self.assertEqual([r["idea"] for r in runs], ["idea one", "idea two"])

    def test_recall_returns_most_similar(self):
        score.save_run("Slack bot that summarizes standups", score.aggregate(uniform(8)), self.bank)
        score.save_run("Real-time translation earbuds", score.aggregate(uniform(4)), self.bank)
        hit = score.recall("a Slack bot that summarizes team threads", self.bank)
        self.assertEqual(hit["idea"], "Slack bot that summarizes standups")

    def test_recall_empty_bank_returns_none(self):
        self.assertIsNone(score.recall("anything", self.bank))


if __name__ == "__main__":
    unittest.main()
