import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import notify  # noqa: E402
import tracker  # noqa: E402


class EvaluateTest(unittest.TestCase):
    def test_triggers_at_threshold(self):
        r = tracker.evaluate("XYZ", "stock", 70.0, [90.0, 100.0, 80.0], 30)
        self.assertEqual(r.drop_pct, 30.0)
        self.assertTrue(r.triggered)

    def test_not_triggered_below_threshold(self):
        r = tracker.evaluate("QQQ", "etf", 71.0, [100.0], 30)
        self.assertFalse(r.triggered)

    def test_price_above_history_counts_as_high(self):
        r = tracker.evaluate("SPY", "etf", 110.0, [100.0], 30)
        self.assertEqual(r.drop_pct, 0.0)
        self.assertEqual(r.high, 110.0)


class CheckFallbackTest(unittest.TestCase):
    def test_falls_back_then_reports_error(self):
        def bad(t, d):
            raise RuntimeError("down")

        def good(t, d):
            return 50.0, [100.0]

        orig = tracker.SOURCES
        try:
            tracker.SOURCES = [bad, good]
            self.assertTrue(tracker.check("VOO", "etf", 30, 365).triggered)
            tracker.SOURCES = [bad]
            r = tracker.check("VOO", "etf", 30, 365)
            self.assertFalse(r.triggered)
            self.assertIn("down", r.error)
        finally:
            tracker.SOURCES = orig


class ConfigTest(unittest.TestCase):
    def test_default_watchlist_has_etfs(self):
        cfg = tracker.load_config(tracker.HERE / "watchlist.json")
        for etf in ("QQQ", "SPY", "VOO"):
            self.assertIn(etf, cfg["etfs"])
        self.assertEqual(cfg["threshold_pct"], 30)


class NotifyTest(unittest.TestCase):
    def test_only_triggered_become_alerts(self):
        data = {"threshold_pct": 30, "lookback_days": 365, "results": [
            {"ticker": "AAA", "kind": "stock", "price": 60, "high": 100, "drop_pct": 40.0, "triggered": True, "error": None},
            {"ticker": "QQQ", "kind": "etf", "price": 95, "high": 100, "drop_pct": 5.0, "triggered": False, "error": None},
        ]}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(data))
            out = notify.alerts(p)
        self.assertEqual([a["ticker"] for a in out], ["AAA"])
        self.assertIn("40.0%", out[0]["title"])


if __name__ == "__main__":
    unittest.main()
