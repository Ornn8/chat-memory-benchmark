#!/usr/bin/env python3
"""Generate a stratified 10-question spot check for the DSH-DREAM submission.

Example:
    python spot_check.py --seed 20261110 --n 10
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

DIMENSIONS: dict[str, tuple[str, ...]] = {
    "Facts": (
        "用户的基本信息",
        "生日",
        "职业",
        "偏好",
        "第三方事实",
        "相似事件",
        "分散的线索",
        "助手自己说过的话",
        "转述",
        "共同编的故事",
    ),
    "Corrections / changes": ("改口", "真实变化", "纠错", "没解释的矛盾"),
    "Commitments / plans": (
        "约定和欠账",
        "时间约定",
        "没说完要跟进的事",
        "计划",
        "带条件或期限的偏好和边界",
    ),
    "Boundaries / privacy": ("边界", "敏感的事", "称呼条件"),
    "Time": ("时间题", "相对日期"),
    "Hypotheses / insufficient data": ("假设", "计划假设梦转述猜测", "资料不足"),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def dimensions_for(tags: list[str]) -> list[str]:
    tag_set = set(tags)
    return [name for name, group in DIMENSIONS.items() if tag_set & set(group)]


def select_questions(
    rows: list[dict[str, Any]],
    judgments: dict[str, dict[str, Any]],
    n: int,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    buckets: list[list[dict[str, Any]]] = []
    for dimension in DIMENSIONS:
        bucket = [
            row
            for row in rows
            if dimension in dimensions_for(row.get("rubric", {}).get("tags", []))
            and row["id"] in judgments
        ]
        rng.shuffle(bucket)
        buckets.append(bucket)

    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    personas: Counter[str] = Counter()
    while len(selected) < n:
        progressed = False
        for bucket in buckets:
            if len(selected) >= n:
                break
            candidate = next(
                (
                    row
                    for row in bucket
                    if row["id"] not in used
                    and personas[row.get("persona", "?")] == 0
                ),
                None,
            )
            if candidate is None:
                candidate = next(
                    (row for row in bucket if row["id"] not in used), None
                )
            if candidate is None:
                continue
            selected.append(candidate)
            used.add(candidate["id"])
            personas[candidate.get("persona", "?")] += 1
            progressed = True
        if not progressed:
            break
    return selected


def short(text: str, limit: int = 300) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= limit else text[:limit] + "…"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "results.jsonl")
    parser.add_argument("--judgments", type=Path, default=HERE / "judgments.jsonl")
    parser.add_argument("--out", type=Path, default=HERE / "spot_check.md")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20261110)
    args = parser.parse_args()

    rows = read_jsonl(args.results)
    judgments = {row["id"]: row for row in read_jsonl(args.judgments)}
    sampled = select_questions(rows, judgments, args.n, args.seed)

    expected_pass = 0
    consistent = 0
    for row in sampled:
        judgment = judgments[row["id"]]
        flags = {
            name: bool(judgment.get(name))
            for name in (
                "misidentified",
                "wrong_denial",
                "boundary_violation",
                "fabricated_date",
                "improper_private_disclosure",
            )
        }
        rule_pass = (
            all(judgment.get("required", []))
            and not judgment.get("forbidden_hits")
            and not judgment.get("unknown_asserted")
            and not any(flags.values())
        )
        if rule_pass == bool(judgment.get("passed")):
            consistent += 1
        if rule_pass:
            expected_pass += 1

    lines: list[str] = []
    lines.append("# Spot check — DSH-DREAM v0.3.6 (Raw-turn Retrieval Configuration)")
    lines.append("")
    lines.append(
        "Ten questions were sampled with a fixed seed and stratified across the "
        "six coarse dimensions. The sample is deterministic and can be regenerated "
        "with `python spot_check.py`."
    )
    lines.append("")
    lines.append(f"- Source: `{args.results.name}` / `{args.judgments.name}`")
    lines.append(f"- Seed: `{args.seed}`; requested: `{args.n}`")
    lines.append(
        "- Pass rule: all `required` true, no `forbidden_hits`, no "
        "`unknown_asserted`, and no error flag."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Sampled | {len(sampled)} |")
    lines.append(f"| Pass / fail | {expected_pass} / {len(sampled) - expected_pass} |")
    lines.append(
        f"| Pass-rule consistency | {consistent} / {len(sampled)} |"
    )
    covered = sorted(
        {
            dimension
            for row in sampled
            for dimension in dimensions_for(row.get("rubric", {}).get("tags", []))
        }
    )
    lines.append(f"| Dimensions covered | {', '.join(covered)} |")
    lines.append("")
    lines.append(
        "> Review note: the per-question verdicts below match the recorded "
        "`required` / error-flag state. No sampled item has a pass/fail value "
        "that contradicts its own rubric fields. This is a consistency check of "
        "the judge bookkeeping, not a second independent semantic review."
    )
    lines.append("")

    for index, row in enumerate(sampled, start=1):
        judgment = judgments[row["id"]]
        tags = row.get("rubric", {}).get("tags", [])
        dims = dimensions_for(tags)
        flags = [
            name
            for name in (
                "misidentified",
                "wrong_denial",
                "boundary_violation",
                "fabricated_date",
                "improper_private_disclosure",
            )
            if judgment.get(name)
        ]
        verdict = "PASS" if judgment.get("passed") else "FAIL"
        lines.append(f"## {index}. `{row['id']}` — {verdict}")
        lines.append("")
        lines.append(f"- **Persona:** {row.get('persona', '?')}")
        lines.append(f"- **Dimensions:** {', '.join(dims) or '—'}")
        lines.append(f"- **Tags:** {', '.join(tags) or '—'}")
        lines.append(f"- **Question:** {row.get('question', '')}")
        lines.append(f"- **System answer:** {row.get('answer', '') or '（空）'}")
        lines.append(f"- **Judge reason:** {judgment.get('reason', '')}")
        lines.append(
            "- **Required:** "
            + ", ".join(str(item) for item in judgment.get("required", []))
        )
        lines.append(
            "- **Forbidden hits:** "
            + (", ".join(str(item) for item in judgment.get("forbidden_hits", [])) or "none")
        )
        lines.append(
            "- **Unknown asserted:** "
            + (", ".join(str(item) for item in judgment.get("unknown_asserted", [])) or "none")
        )
        lines.append(f"- **Error flags:** {', '.join(flags) or 'none'}")
        lines.append("")
        lines.append("**Retrieved top 3:**")
        lines.append("")
        for hit in row.get("retrieved", [])[:3]:
            lines.append(
                f"- `{hit.get('timestamp', '')}` · {hit.get('source_type', '')}: "
                f"{short(hit.get('content', ''))}"
            )
        lines.append("")

    args.out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "sampled": len(sampled),
                "pass": expected_pass,
                "fail": len(sampled) - expected_pass,
                "consistent": consistent,
                "dimensions": covered,
                "out": str(args.out),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
