import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / 'results' / 'submissions' / 'pmem-0.41.0-2026-11-09'


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


class PmemSubmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key_ids = {
            json.loads(line)['id']
            for line in (ROOT / 'datasets/natural-timegrid-20261101-v2/review-only/answer-key.jsonl')
            .read_text(encoding='utf-8').splitlines() if line.strip()
        }
        cls.summary = json.loads((SUB / 'summary.json').read_text(encoding='utf-8'))

    def test_answers_cover_the_formal_set(self):
        self.assertEqual(len(self.key_ids), 714)
        for name in ('answers.jsonl', 'control-answers.jsonl'):
            with self.subTest(file=name):
                answers = rows(SUB / name)
                self.assertEqual(len(answers), 714)
                self.assertEqual(len({row['id'] for row in answers}), 714)
                self.assertTrue({row['id'] for row in answers} <= self.key_ids)
                for row in answers:
                    self.assertIn('answer', row)
                    self.assertIsInstance(row['answer'], str)

    def test_reviews_and_judgments_match_answers(self):
        cases = [
            ('reviews.jsonl', 'judgments.jsonl', 'answers.jsonl', 714),
            ('control-reviews.jsonl', 'control-judgments.jsonl', 'control-answers.jsonl', 713),
        ]
        for reviews_name, judgments_name, answers_name, judged in cases:
            with self.subTest(arm=answers_name):
                answers = {row['id'] for row in rows(SUB / answers_name)}
                reviews = rows(SUB / reviews_name)
                judgments = rows(SUB / judgments_name)
                self.assertEqual(len(reviews), judged)
                self.assertEqual(len(judgments), judged)
                self.assertEqual({row['id'] for row in reviews}, {row['id'] for row in judgments})
                self.assertTrue({row['id'] for row in reviews} <= answers)
                for row in judgments:
                    self.assertIn('pass', row)

    def test_summary_matches_artifacts(self):
        pmem = self.summary['systems']['pmem-0.41.0']
        control = self.summary['systems']['pmem-0.41.0-no-enhance']
        self.assertEqual(pmem['overall'], {'passed': 618, 'total': 714})
        self.assertEqual(control['overall'], {'passed': 583, 'total': 713})
        # 判分汇总与 summary 一致
        grading = json.loads((SUB / 'grading-summary.json').read_text(encoding='utf-8'))
        self.assertEqual(grading['passed'], pmem['overall']['passed'])
        self.assertEqual(grading['scored'], pmem['overall']['total'])
        grading_control = json.loads((SUB / 'control-grading-summary.json').read_text(encoding='utf-8'))
        self.assertEqual(grading_control['passed'], control['overall']['passed'])
        self.assertEqual(grading_control['scored'], control['overall']['total'])
        # 分项自洽
        for system in (pmem, control):
            self.assertEqual(sum(v['total'] for v in system['intervals'].values()), system['overall']['total'])
            self.assertEqual(
                sum(v['whole_answer_passed'] for v in system['intervals'].values()),
                system['overall']['passed'],
            )
            self.assertEqual(len(system['topics']), 27)
            for topic in system['topics'].values():
                self.assertEqual(sum(cell['total'] for cell in topic['cells']), topic['total'])
                self.assertEqual(
                    sum(cell['whole_answer_passed'] for cell in topic['cells']),
                    topic['whole_answer_passed'],
                )
        # 消融与配对题数
        both = self.summary['ablation']['both']
        self.assertEqual(both['net'], both['treatment'] - both['control'])
        self.assertEqual(both['treatment'], 618)
        self.assertLess(both['mcnemar_p'], 0.01)
        # 与其它 714 卷共用同一题库指纹
        reference = json.loads(
            (ROOT / 'results/2026-11-05-suzu-forced-summary.json').read_text(encoding='utf-8')
        )
        self.assertEqual(self.summary['question_set_sha256'], reference['question_set_sha256'])

    def test_submission_readme_states_config(self):
        text = (SUB / 'README.md').read_text(encoding='utf-8')
        for needle in ('618 / 714', '583 / 713', 'baseline-618', 'deepseek-v4.1-flash', 'rawline'):
            self.assertIn(needle, text)
        # 材料清单里点名的文件都真的在
        for name in ('answers.jsonl', 'reviews.jsonl', 'judgments.jsonl', 'grading-summary.json',
                     'control-answers.jsonl', 'control-reviews.jsonl', 'control-judgments.jsonl',
                     'control-grading-summary.json', 'summary.json'):
            self.assertIn(name, text)
            self.assertTrue((SUB / name).is_file(), name)


if __name__ == '__main__':
    unittest.main()
