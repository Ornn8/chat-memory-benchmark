import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'benchmark-2.1'
sys.path.insert(0, str(B / 'harness'))

from bench21 import natural, scoring  # noqa: E402
from bench21.systems import AlwaysRecall, Bm25Local, FullContext, IncBM25, RecentN, TailOnly  # noqa: E402

DATA = B / 'natural' / 'dataset'


def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def turn(n, user='你好', assistant='嗯'):
    return {'turn': n, 'time': f'2026-09-01T{(n % 24):02d}:00:00+08:00', 'user': user, 'assistant': assistant}


def key(cls, sub, sev='普通'):
    return {'class': cls, 'subtype': sub, 'severity': sev, 'emotion': 'neutral'}


class TurnScoreTests(unittest.TestCase):
    def test_x_scores(self):
        k = key('X', 'X1')
        self.assertEqual(natural.turn_score(k, {'responsive': True, 'target_recalled': False}), 0.0)
        self.assertAlmostEqual(natural.turn_score(k, {'responsive': True, 'target_recalled': True, 'target_content': 'correct', 'naturalness': 2}), 1.0)
        self.assertAlmostEqual(natural.turn_score(k, {'responsive': True, 'target_recalled': True, 'target_content': 'correct', 'naturalness': 0}), 0.8)
        self.assertAlmostEqual(natural.turn_score(k, {'responsive': True, 'target_recalled': True, 'target_content': 'wrong', 'naturalness': 2}), 0.2)
        self.assertEqual(natural.turn_score(k, {'responsive': True, 'target_recalled': True, 'target_content': 'correct', 'naturalness': 2, 'fabrication': True}), 0.0)

    def test_y_and_n0(self):
        self.assertEqual(natural.turn_score(key('Y', 'Y1'), {'responsive': True, 'forbidden_recalled': True}), 0.0)
        self.assertAlmostEqual(natural.turn_score(key('Y', 'Y2'), {'responsive': True, 'forbidden_recalled': True}), 0.2)
        self.assertEqual(natural.turn_score(key('Y', 'Y3'), {'responsive': True, 'forbidden_recalled': False}), 1.0)
        self.assertEqual(natural.turn_score(key('Y', 'Y3'), {'responsive': False, 'forbidden_recalled': False}), 0.0)   # silence is not restraint
        self.assertAlmostEqual(natural.turn_score(key('N0', 'N0'), {'responsive': True, 'other_recalls': ['x']}), 0.4)

    def test_h_and_z(self):
        self.assertEqual(natural.turn_score(key('H', 'H2'), {'responsive': True, 'hedged': True}), 1.0)
        self.assertEqual(natural.turn_score(key('H', 'H1'), {'responsive': True, 'target_recalled': True, 'target_content': 'correct'}), 0.7)
        self.assertEqual(natural.turn_score(key('H', 'H2'), {'responsive': True, 'target_recalled': True, 'target_content': 'correct'}), 0.0)
        self.assertEqual(natural.turn_score(key('Z', 'Z1'), {'responsive': True}), 1.0)
        self.assertEqual(natural.turn_score(key('Z', 'Z1'), {'responsive': True, 'any_recall': True, 'naturalness': 0}), 0.5)


class AggregateTests(unittest.TestCase):
    def test_class_weights_sum_to_one_and_repeat_cap(self):
        self.assertAlmostEqual(sum(natural.CLASS_WEIGHT.values()), 1.0)
        probes = [{'id': 'p1'}]
        k = {'p1': key('Y', 'Y2')}
        js = [{'id': 'p1', 'k': 0, 'score': 1.0, 'judge': {'forbidden_recalled': True}},
              {'id': 'p1', 'k': 1, 'score': 1.0, 'judge': {'forbidden_recalled': True}},
              {'id': 'p1', 'k': 2, 'score': 1.0, 'judge': {}}, {'id': 'p1', 'k': 3, 'score': 1.0, 'judge': {}}]
        self.assertLessEqual(natural.item_scores(probes, k, js)['p1'], 0.3)

    def test_severe_counts_double(self):
        probes = [{'id': 'a'}, {'id': 'b'}]
        k = {'a': key('X', 'X1', '严重'), 'b': key('X', 'X1')}
        js = [{'id': 'a', 'k': 0, 'score': 1.0, 'judge': {'responsive': True, 'target_recalled': True}},
              {'id': 'b', 'k': 0, 'score': 0.0, 'judge': {'responsive': True, 'target_recalled': False}}]
        agg, _ = natural.aggregate(probes, k, js)
        self.assertAlmostEqual(agg['by_class']['X'], 100 * 2 / 3, places=1)


class RewindTests(unittest.TestCase):
    def test_bm25_truncate(self):
        bm = IncBM25()
        for t in (turn(1, '喜欢猫'), turn(2, '喜欢狗'), turn(3, '汤团爱喝水')):
            bm.add(t['user'])
        before = (len(bm.dl), bm.total)
        bm.add('尾巴里的独特词语')
        bm.truncate(3)
        self.assertEqual((len(bm.dl), bm.total), before)
        self.assertEqual(bm.top('独特词语', 3), [])

    def test_systems_rewind_to_mark(self):
        for s in (Bm25Local(), RecentN(6), FullContext(), TailOnly(), AlwaysRecall()):
            for i in range(1, 10):
                s.ingest(turn(i, f'第{i}轮'))
            tok = s.mark()
            if hasattr(s, 'begin_tail'):
                s.begin_tail()
            s.ingest(turn(10, '尾巴里的话'))
            s.rewind(tok)
            self.assertEqual(s.mark(), tok, s.name)
            r = s.retrieve('第3轮', '2026-09-02T10:00:00+08:00', 9)
            self.assertNotIn('尾巴里的话', r.prompt, s.name)

    def test_never_recall_sees_only_the_tail(self):
        s = TailOnly()
        for i in range(1, 6):
            s.ingest(turn(i, f'旧历史{i}'))
        s.begin_tail()
        s.ingest(turn(6, '当前的话'))
        p = s.retrieve('q', '2026-09-02T10:00:00+08:00', 6).prompt
        self.assertIn('当前的话', p)
        self.assertNotIn('旧历史', p)


class DatasetTests(unittest.TestCase):
    def test_dev_set_shape(self):
        probes, keys = jl(DATA / 'natural-probes-dev.jsonl'), jl(DATA / 'natural-key-dev.jsonl')
        self.assertEqual(len(probes), 34)
        self.assertEqual({p['id'] for p in probes}, {k['id'] for k in keys})
        for p in probes:
            self.assertEqual(p['split'], 'dev')
            self.assertIn(p['tier'], 'AB')
            ts = [t['time'] for t in p.get('tail', [])] + ([p['probe']['time']] if p['tier'] == 'A' else [s['time'] for s in p['script']])
            self.assertEqual(ts, sorted(ts), p['id'])
            if p['tier'] == 'B':
                self.assertEqual(len(p['script']), 4)

    def test_sealed_commitment(self):
        c = json.load(open(DATA / 'natural-sealed-commitment.json', encoding='utf-8'))
        self.assertEqual(c['n_sealed'], 134)
        self.assertEqual(len(c['items']), 134)
        self.assertTrue(all(re.fullmatch(r'[0-9a-f]{64}', v) for v in c['items'].values()))
        self.assertFalse(set(c['items']) & {p['id'] for p in jl(DATA / 'natural-probes-dev.jsonl')})

    def test_no_card_leak_in_probe_view(self):
        for p in jl(DATA / 'natural-probes-dev.jsonl'):
            self.assertFalse({'target', 'forbidden', 'decoys', 'evidence', 'reference_reply'} & set(p))

    def test_x_probes_do_not_name_the_target(self):
        keys = {k['id']: k for k in jl(DATA / 'natural-key-dev.jsonl')}
        for p in jl(DATA / 'natural-probes-dev.jsonl'):
            k = keys[p['id']]
            if k['class'] != 'X':
                continue
            text = ' '.join([t['user'] + t['assistant'] for t in p.get('tail', [])] + [p['probe']['user']])
            for term in k.get('terms_absent') or []:
                self.assertNotIn(term, text, p['id'])

    def test_tails_do_not_copy_history_lines(self):
        hist = {}
        for persona in ('M01', 'M02'):
            f = B / 'dataset' / 'histories' / f'{persona}.jsonl'
            hist[persona] = {x.strip() for r in jl(f) for x in r['用户消息'].split('\n') if len(x.strip()) >= 14}
        for p in jl(DATA / 'natural-probes-dev.jsonl'):
            texts = [t['user'] for t in p.get('tail', [])] + ([p['probe']['user']] if p['tier'] == 'A' else [s['user'] for s in p['script']])
            for t in texts:
                for line in t.split('\n'):
                    self.assertNotIn(line.strip(), hist[p['persona']], p['id'])


class ConfigTests(unittest.TestCase):
    def test_board_weights_and_floors(self):
        w = scoring.CONFIG['board_weights']
        self.assertAlmostEqual(w['short'] + w['long'] + w['natural'], 1.0)
        self.assertEqual((w['short'], w['long'], w['natural']), (0.375, 0.375, 0.25))
        self.assertEqual((scoring.CONFIG['floor_restraint_pct'], scoring.CONFIG['floor_fabrication_pct']), (70.0, 5.0))
        self.assertEqual(scoring.CONFIG['cost_coef'], 3.0)
        self.assertEqual(scoring.CONFIG['cost_floor_ratio'], 0.25)


if __name__ == '__main__':
    unittest.main()
