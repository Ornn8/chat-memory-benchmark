import json
import re
import unittest
from pathlib import Path

from grading import grade


class SurfcoreBgeM3AuthorSubmissionTest(unittest.TestCase):
    prefix = '2026-11-07-surfcore-bge-m3-vector'

    def _result(self):
        return Path(__file__).resolve().parents[1] / 'results'

    def test_recomputes_from_answers_and_reviews(self):
        result = self._result()
        answers = grade.indexed(grade.read_rows(result / (self.prefix + '-answers.jsonl')))
        packets = grade.indexed(list(grade.prepare(answers.values())))
        reviews = grade.indexed(grade.read_rows(result / (self.prefix + '-reviews.jsonl')))
        self.assertEqual(len(answers), 714)
        self.assertEqual(len(packets), 714)
        self.assertEqual(len(reviews), 714)
        judged = list(grade.score(packets, reviews))
        self.assertEqual((len(judged), sum(row['pass'] for row in judged)), (714, 605))

    def test_saved_summary_matches_recomputed_grading(self):
        result = self._result()
        answers = grade.indexed(grade.read_rows(result / (self.prefix + '-answers.jsonl')))
        packets = grade.indexed(list(grade.prepare(answers.values())))
        reviews = grade.indexed(grade.read_rows(result / (self.prefix + '-reviews.jsonl')))
        report = grade.summarize(list(grade.score(packets, reviews)))
        saved = json.loads((result / (self.prefix + '-grading-summary.json')).read_text(encoding='utf-8'))
        self.assertEqual(
            {key: saved[key] for key in ('passed', 'scored', 'dataset_questions', 'groups')},
            report,
        )

    def test_report_matches_summary(self):
        result = self._result()
        saved = json.loads((result / (self.prefix + '-grading-summary.json')).read_text(encoding='utf-8'))
        self.assertEqual(saved['dataset_questions'], 714)
        self.assertEqual((saved['passed'], saved['scored']), (605, 714))
        self.assertEqual(sum(x['passed'] for x in saved['groups']['persona'].values()), 605)
        text = (result / (self.prefix + '.md')).read_text(encoding='utf-8')
        self.assertRegex(
            text,
            re.compile(r'^\| 官方 judge prompt \+ `grade\.py` 校验汇总 \| 605 / 714 \|$', re.MULTILINE),
        )
        for label, counts in saved['groups']['content_tags'].items():
            pattern = rf'^\| {re.escape(label)} \| {counts["passed"]} / {counts["total"]} \|$'
            self.assertRegex(text, re.compile(pattern, re.MULTILINE))
        for days, counts in saved['groups']['interval_days'].items():
            pattern = rf'^\| {days} 天 \| {counts["passed"]} / {counts["total"]} \|$'
            self.assertRegex(text, re.compile(pattern, re.MULTILINE))


if __name__ == '__main__':
    unittest.main()
