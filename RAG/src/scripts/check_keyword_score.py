"""
キーワードスコアリング確認スクリプト

search/scorer.py の calc_keyword_score を単体で実行し、
カバレッジ・密度・サイズペナルティの内訳を確認する。
LLMが抽出したキーワードが PIR テキストにどれほどマッチするかを素早く検証できる。

使用例:
    cd Lightz-System1/backend
    uv run python ../../factors/構造化use/check_keyword_score.py \
        --text "ボルトを規定トルクで締め付ける。ファスナの取付を確認する。" \
        --keywords "ボルト" "トルク" "ファスナ" "取付"

    # PIR JSONから全テキストを読み込んでスコアを一覧表示
    uv run python ../../factors/構造化use/check_keyword_score.py \
        --pir path/to/pir.json \
        --keywords "ボルト" "トルク" "取付"
"""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Lightz-System1" / "backend"))

from refactored.search.scorer import SearchScorer


def _extract_texts_from_json(pir_json: dict) -> list[tuple[str, str, str]]:
    """PIR JSONから (step, path, text) のリストを再帰的に抽出"""
    results = []

    def walk(node: dict, path: str):
        step = node.get("手順記号", "")
        for i, line in enumerate(node.get("作業内容", [])):
            results.append((step, f"{path}:{i}", line))
        for j, sub in enumerate(node.get("sub_steps", [])):
            walk(sub, f"{path}/sub{j}")

    for i, s in enumerate(pir_json.get("steps", [])):
        walk(s, f"step{i}")

    return results


def score_text(text: str, keywords: list[str], scorer: SearchScorer) -> tuple[float, list[str]]:
    return scorer.calc_keyword_score(text, keywords)


def main():
    parser = argparse.ArgumentParser(description="キーワードスコアリング確認")
    parser.add_argument("--text", help="スコアリング対象テキスト（直接指定）")
    parser.add_argument("--pir", help="PIR JSONファイルのパス（全チャンクをスコアリング）")
    parser.add_argument("--keywords", nargs="+", required=True, help="キーワードリスト")
    parser.add_argument("--min-score", type=float, default=0.0, help="表示する最低スコア（デフォルト: 0.0）")
    parser.add_argument("--top", type=int, default=20, help="表示件数上限（デフォルト: 20）")
    args = parser.parse_args()

    scorer = SearchScorer()
    keywords = args.keywords

    print(f"\nキーワード ({len(keywords)} 個): {keywords}")
    kw_count = max(len(keywords), 1)
    size_penalty = min(1.0, math.log(kw_count + 1) / math.log(16))
    print(f"サイズペナルティ: {size_penalty:.4f}  (log({kw_count}+1)/log(16))\n")

    if args.text:
        # 単一テキストのスコアリング
        score, hits = score_text(args.text, keywords, scorer)
        coverage = len(hits) / len(keywords) if keywords else 0
        hit_chars = sum(args.text.count(h) * len(h) for h in hits)
        density = hit_chars / max(len(args.text), 1)

        print(f"テキスト   : {args.text}")
        print(f"ヒット語   : {hits}")
        print(f"カバレッジ : {coverage:.4f}  ({len(hits)}/{len(keywords)})")
        print(f"密度       : {density:.4f}  ({hit_chars}/{len(args.text)} 文字)")
        print(f"基本スコア : {(coverage + density) / 2:.4f}")
        print(f"ペナルティ : {size_penalty:.4f}")
        print(f"最終スコア : {score:.4f}")

    elif args.pir:
        # PIR全チャンクのスコアリング
        pir_path = Path(args.pir)
        if not pir_path.exists():
            print(f"[ERROR] PIRファイルが見つかりません: {pir_path}")
            sys.exit(1)

        with open(pir_path, encoding="utf-8") as f:
            pir_json = json.load(f)

        texts = _extract_texts_from_json(pir_json)
        print(f"PIR: {pir_path.name}  チャンク数: {len(texts)}\n")

        scored = []
        for step, path, text in texts:
            score, hits = score_text(text, keywords, scorer)
            if score >= args.min_score:
                scored.append((score, step, path, text, hits))

        scored.sort(reverse=True)

        print(f"スコア >= {args.min_score} の件数: {len(scored)} 件（上位 {args.top} 件を表示）\n")
        for rank, (score, step, path, text, hits) in enumerate(scored[:args.top], 1):
            print(f"  [{rank}] score={score:.4f}  step={step}  path={path}")
            print(f"       text : {text[:80]}")
            print(f"       hits : {hits}")
            print()
    else:
        parser.print_help()
        print("\n[ERROR] --text か --pir のどちらかを指定してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
