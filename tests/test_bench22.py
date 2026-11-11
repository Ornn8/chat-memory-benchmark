import json
import math
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'benchmark-2.2' / 'harness'))

from bench22 import scoring, gateway  # noqa: E402

DAY = 86400


def it(i, age, tw=None, kind="main", sev="normal", pt="regular"):
    return {"id": i, "kind": kind, "twin_id": tw, "group_age_seconds": age, "rubric": {"severity": sev}, "probe_type": pt}


class ScoringTests(unittest.TestCase):
    def test_pair_needs_both_and_control_alone_gives_nothing(self):
        items = [it("G1/a", 100, tw="T1", pt="due_day"), it("G1/b", 100, tw="T1", pt="no_due_control"), it("G2/a", 100), it("G3/x", 100, kind="control")]
        units = scoring.build_units(items)
        self.assertEqual(len(units), 2)                              # one pair + one single; the lone control is not scored
        self.assertEqual(scoring.board_scores(units, {"G1/a": True, "G1/b": False, "G2/a": True})["pass_pct"], 50.0)
        self.assertEqual(scoring.board_scores(units, {"G1/a": True, "G1/b": True, "G2/a": True})["pass_pct"], 100.0)
        self.assertEqual(scoring.board_scores(units, {"G1/a": False, "G1/b": True, "G2/a": False})["pass_pct"], 0.0)

    def test_a_is_mean_of_daily_and_long(self):
        items = [it("G1/a", 60), it("G2/a", 3600), it("G3/a", 5 * DAY), it("G4/a", 40 * DAY), it("G5/a", 40 * DAY), it("G6/a", 40 * DAY)]
        passed = {"G1/a": True, "G2/a": True, "G3/a": True, "G4/a": False, "G5/a": False, "G6/a": False}
        b = scoring.board_scores(scoring.build_units(items), passed)
        self.assertAlmostEqual(b["D"], 100.0)
        self.assertAlmostEqual(b["L"], 25.0)
        self.assertAlmostEqual(b["A"], 62.5)                         # not the item-weighted 4/6

    def test_boundary_is_one_day(self):
        us = scoring.build_units([it("G1/a", DAY), it("G2/a", DAY + 1)])
        self.assertEqual({u["key"]: u["bucket"] for u in us}, {"G1/a": "daily", "G2/a": "long"})

    def test_severe_counts_double(self):
        items = [it("G1/a", 60, sev="severe"), it("G2/a", 60)]
        b = scoring.board_scores(scoring.build_units(items), {"G1/a": True, "G2/a": False})
        self.assertAlmostEqual(b["D"], 100 * 2 / 3)

    def test_pair_age_is_the_older_member(self):
        us = scoring.build_units([it("G1/a", 60, tw="T"), it("G1/b", 9 * DAY, tw="T")])
        self.assertEqual(us[0]["bucket"], "long")

    def test_composite_and_floor(self):
        self.assertAlmostEqual(scoring.composite(50, 10, 10), 50)
        self.assertAlmostEqual(scoring.composite(50, 20, 10), 47)
        self.assertAlmostEqual(scoring.composite(50, 5, 10), 53)
        self.assertAlmostEqual(scoring.composite(50, 0, 10), 56)

    def test_bootstrap_clusters_by_group(self):
        # 40 groups x 5 questions; whole groups pass or fail together => wide interval; independent => narrow
        items, passed = [], {}
        for g in range(40):
            for k in range(5):
                i = f"M01-G{g:03d}/q{k}"
                items.append(it(i, 3 * DAY))
                passed[i] = (g % 2 == 0)
        units = scoring.build_units(items)
        ci = scoring.bootstrap_A(units, passed, n_boot=500)
        self.assertLess(ci["lo"], 50)
        self.assertGreater(ci["hi"], 50)
        self.assertGreater(ci["hi"] - ci["lo"], 10)                  # 40 clusters: sd ~ 8 points
        indep = {u["ids"][0]: ((int(u["ids"][0][-1]) + int(u["ids"][0][5:8])) % 2 == 0) for u in units}
        ci2 = scoring.bootstrap_A(units, indep, n_boot=500)
        self.assertLess(ci2["hi"] - ci2["lo"], ci["hi"] - ci["lo"])

    def test_composite_interval_weights(self):
        b = {"short": {"draws": [50.0] * 10, "S_shift": 0.0}, "long": {"draws": [60.0] * 10, "S_shift": 0.0}, "natural": {"draws": [40.0] * 10, "S_shift": 0.0}}
        lo, hi = scoring.composite_interval(b, {"short": 0.25, "long": 0.25, "natural": 0.5})
        self.assertAlmostEqual(lo, 47.5)
        self.assertAlmostEqual(hi, 47.5)


class CeilingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        gateway.State.ledger = gateway.Ledger(os.path.join(self.tmp.name, "l.jsonl"))
        gateway.State.cache = gateway.Cache(os.path.join(self.tmp.name, "c.sqlite3"))
        gateway.State.cap_usd = 100.0
        gateway.State.entry_cost = None
        gateway.State.entry_ceiling_cny = 1.0
        gateway.State.eval_token = ""
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), gateway.H)
        self.srv.daemon_threads = True
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.srv.server_address[1]}"

    def tearDown(self):
        self.srv.shutdown()
        gateway.State.cache.db.close()
        self.tmp.cleanup()

    def post(self, phase, tin, system="x:M01:sealed", token=None):
        body = json.dumps({"model": "deepseek-v4.1-flash", "in_tokens": tin, "out_tokens": 0}).encode()
        h = {"Content-Type": "application/json", "X-Bench-Run": "t", "X-Bench-System": system, "X-Bench-Phase": phase}
        if token:
            h["X-Bench-Eval-Token"] = token
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + "/v1/charge", data=body, headers=h, method="POST")) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_entry_calls_stop_at_ceiling(self):
        # 1 million flash input tokens = CNY 1.296 > ceiling 1.0
        self.assertEqual(self.post("ingest", 500_000)[0], 200)         # 0.648
        self.assertEqual(self.post("retrieve", 500_000)[0], 200)       # 1.296 total -> now over the ceiling
        code, body = self.post("retrieve", 10)
        self.assertEqual(code, 403)
        self.assertEqual(body["code"], "ENTRY_COST_CEILING")
        self.assertEqual(self.post("ingest", 10, system="other:M01:sealed")[0], 200)   # other entries unaffected

    def test_evaluator_calls_do_not_count_and_are_not_blocked(self):
        for _ in range(5):
            self.assertEqual(self.post("answer", 500_000)[0], 200)     # development mode: phase decides, answer is ours
        self.assertEqual(self.post("ingest", 10)[0], 200)

    def test_token_decides_when_configured(self):
        gateway.State.eval_token = "secret"
        for _ in range(3):
            self.assertEqual(self.post("answer", 500_000, token="secret")[0], 200)    # evaluator: free of the ceiling
        self.assertEqual(self.post("answer", 700_000)[0], 200)         # no token, phase header claims 'answer': still the entry's
        self.assertEqual(self.post("answer", 700_000)[0], 200)
        self.assertEqual(self.post("answer", 10)[0], 403)

    def test_ceiling_survives_restart(self):
        self.post("ingest", 800_000)
        self.post("ingest", 800_000)
        gateway.State.entry_cost = None                                  # as after a gateway restart: rebuilt from the ledger
        self.assertEqual(self.post("retrieve", 10)[0], 403)


if __name__ == "__main__":
    unittest.main()


class NaturalTests(unittest.TestCase):
    def test_interval_and_x_diagnostics(self):
        from bench22 import natural
        probes, key, judg, turns = [], {}, [], []
        for i in range(12):
            pid = f"P{i}"
            cls = "X" if i < 6 else "Y"
            probes.append({"id": pid, "persona": "M01", "tier": "A", "split": "sealed"})
            key[pid] = {"id": pid, "class": cls, "subtype": "X4" if i < 2 else cls + "1", "severity": "普通", "emotion": "neutral", "case_id": f"G{i // 2}",
                        "evidence": f"- 第{100 + i}轮 2026-09-01 user：x" if cls == "X" else ""}
            hit = i % 2 == 0
            judg.append({"id": pid, "k": 0, "score": 0.8 if (cls == "X" and hit) else (0.0 if cls == "X" else 1.0),
                         "judge": {"target_recalled": cls == "X" and hit, "responsive": True, "forbidden_recalled": False, "fabrication": False}})
            turns.append({"id": pid, "k": 0, "used_turns": [100 + i] if i % 3 != 2 else [1], "leak_turns_after_visible": [], "mem_tokens": 10, "prompt": "x"})
        agg, sc = natural.aggregate(probes, key, judg, turns, n_boot=200)
        self.assertIn("A_nat_interval95", agg)
        lo, hi = agg["A_nat_interval95"]
        self.assertLessEqual(lo, agg["A_nat"] + 0.01)
        self.assertGreaterEqual(hi, agg["A_nat"] - 0.01)
        d = agg["x_diagnostics"]
        self.assertEqual(d["n_X"], 6)
        self.assertEqual(d["n_reached"], 4)                      # probes 2 and 5 did not retrieve their evidence turn
        self.assertEqual(d["used_when_reached_pct"], 50.0)       # reached = 0,1,3,4; recalled = even ids = 0 and 4
