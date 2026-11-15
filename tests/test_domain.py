from pathlib import Path
import unittest

from agent import run
from loop import Replay

ROOT = Path(__file__).resolve().parents[1] / "examples"
PROBES = ["population", "quality", "freshness"]


class DriftTest(unittest.TestCase):
    def test_feature_shift_is_quantified_and_has_separate_quality_evidence(self):
        result = run(ROOT / "main.json", Replay(PROBES))
        drift = result["evidence"]["population"]["data"]["drifted"][0]
        self.assertEqual(drift["feature"], "checkout_value")
        self.assertGreaterEqual(drift["psi"], 0.25)
        self.assertEqual(result["evidence"]["quality"]["data"], {"baseline": 0.94, "current": 0.79})

    def test_shift_without_quality_loss_is_only_a_watch(self):
        result = run(ROOT / "shift-only.json", Replay(PROBES))
        self.assertEqual(result["decision"], "watch")
