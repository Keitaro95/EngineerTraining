#!/usr/bin/env python3
"""メッセージ履歴から相手の恋愛態度を 0（拒絶）〜4（付き合いたい）で評価する。

  python main.py data/sample_messages.jsonl
  python main.py data/log.jsonl --since 2026-06-01     # 期間を絞る
  python main.py data/log.jsonl --json                 # 機械可読な出力
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from affinity import load_messages, render
from affinity.schema import SchemaError
from affinity.scoring import judge


def _parse_date(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"日付として読めません: {value}（例 2026-06-01）")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="メッセージ履歴（JSONL または JSON 配列）")
    parser.add_argument("--since", type=_parse_date, help="この日以降のメッセージのみ評価")
    parser.add_argument("--until", type=_parse_date, help="この日以前のメッセージのみ評価")
    parser.add_argument("--json", action="store_true", help="JSON で出力")
    args = parser.parse_args(argv)

    try:
        messages = load_messages(args.path)
    except (SchemaError, OSError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    if args.since:
        messages = [m for m in messages if m.timestamp >= args.since]
    if args.until:
        messages = [m for m in messages if m.timestamp <= args.until]

    if not messages:
        print("エラー: 条件に合うメッセージがありません", file=sys.stderr)
        return 1

    verdict = judge(messages)

    if args.json:
        print(json.dumps({
            "level": verdict.level,
            "label": verdict.label,
            "score": round(verdict.score, 3),
            "confidence": verdict.confidence,
            "confidence_reasons": verdict.confidence_reasons,
            "content_signal": verdict.content_signal,
            "behavior_signal": verdict.behavior_signal,
            "behavior_coverage": round(verdict.behavior_coverage, 3),
            "decisive_notes": verdict.decisive_notes,
            "metrics": [
                {"key": m.key, "label": m.label, "value": m.value,
                 "score": m.score, "sample_size": m.sample_size, "detail": m.detail}
                for m in verdict.behavior.metrics
            ],
        }, ensure_ascii=False, indent=2))
    else:
        print(render(verdict))

    return 0


if __name__ == "__main__":
    sys.exit(main())
