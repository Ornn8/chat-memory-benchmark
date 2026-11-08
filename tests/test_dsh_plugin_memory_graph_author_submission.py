# -*- coding: utf-8 -*-
"""校验 dsh-plugin-memory-graph 作者侧提交：答卷/初判覆盖全题库，报告表格与汇总 JSON 一致。"""
import json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATE = '2026-11-07'
SLUG = 'dsh-plugin-memory-graph'
SUBDIR = 'dsh-plugin-memory-graph-2026-11-07'

def _rows(name):
    return [json.loads(l) for l in (ROOT / 'results' / 'submissions' / SUBDIR / name).read_text(encoding='utf-8').splitlines() if l.strip()]

class TestDaifeiyuSubmission(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads((ROOT / 'results' / 'submissions' / SUBDIR / 'summary.json').read_text(encoding='utf-8'))
        self.md = (ROOT / 'results' / 'submissions' / SUBDIR / 'README.md').read_text(encoding='utf-8')

    def test_answers_cover_all_questions(self):
        rows = _rows('answers.jsonl')
        self.assertEqual(len(rows), self.summary['dataset_questions'])
        self.assertEqual(len({r['id'] for r in rows}), len(rows))

    def test_reviews_cover_all_questions(self):
        rows = _rows('reviews.jsonl')
        self.assertEqual(len(rows), self.summary['scored'])
        self.assertEqual(len({r['id'] for r in rows}), len(rows))

    def test_report_matches_summary(self):
        s = self.summary
        self.assertIn('%d / %d' % (s['passed'], s['scored']), self.md)
        for g in s['groups']['persona'].values():
            self.assertIn('%d / %d' % (g['passed'], g['total']), self.md)
        for g in s['groups']['interval_days'].values():
            self.assertIn('%d / %d' % (g['passed'], g['total']), self.md)
        for g in s['groups']['content_tags'].values():
            self.assertIn('%d / %d' % (g['passed'], g['total']), self.md)

if __name__ == '__main__':
    unittest.main()

    def test_judgments_consistent_with_summary(self):
        rows = _rows('judgments.jsonl')
        self.assertEqual(len(rows), self.summary['scored'])
        self.assertEqual(sum(int(r['pass']) for r in rows), self.summary['passed'])
        self.assertEqual(len({r['id'] for r in rows}), len(rows))
