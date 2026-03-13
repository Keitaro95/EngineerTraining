"""
Embedding 類似度チェックスクリプト

2つのテキスト間のコサイン類似度を計算し、RAG閾値との比較を確認する。
「なぜこの文がヒットしないのか」「類義語展開の効果」を手軽に検証できる。

使用例:
    cd Lightz-System1/backend
    uv run python ../../factors/構造化use/check_embedding_similarity.py \
        "ボルトを取り外す" "ファスナを除去する"

    # 複数ペアを一括比較（--pairs-file で JSONを渡す）
    uv run python ../../factors/構造化use/check_embedding_similarity.py \
        --pairs-file ../../factors/構造化use/sample_pairs.json

pairs-file フォーマット:
    [
      ["ボルトを取り外す", "ファスナを除去する"],
      ["トルクレンチで締め付ける", "規定トルクで締付"]
    ]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Lightz-System1" / "backend"))

from refactored.rag.embeddings import get_embedding_model
from refactored.config.settings import Settings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """L2正規化済みベクトルのコサイン類似度（= dot積）"""
    return float(np.dot(a, b))


def compare(text_a: str, text_b: str, model, threshold: float) -> float:
    embs = model.encode([text_a, text_b], normalize_embeddings=True, show_progress_bar=False)
    sim = cosine_similarity(embs[0], embs[1])

    ok = sim >= threshold
    flag = "✅ ヒット" if ok else "❌ 閾値未満"
    print(f"  {flag}  sim={sim:.4f}  (threshold={threshold})")
    print(f"    A: {text_a}")
    print(f"    B: {text_b}")
    print()
    return sim


def main():
    parser = argparse.ArgumentParser(description="Embedding 類似度チェック")
    parser.add_argument("texts", nargs="*", help="比較する2つのテキスト（positional）")
    parser.add_argument("--pairs-file", help="比較ペアのJSONファイル（省略可）")
    parser.add_argument("--threshold", type=float, default=0.80, help="RAG閾値（デフォルト: 0.80）")
    args = parser.parse_args()

    # ペアの収集
    pairs: list[tuple[str, str]] = []

    if args.pairs_file:
        with open(args.pairs_file, encoding="utf-8") as f:
            raw = json.load(f)
        for item in raw:
            pairs.append((item[0], item[1]))
    elif len(args.texts) == 2:
        pairs.append((args.texts[0], args.texts[1]))
    else:
        parser.print_help()
        print("\n[ERROR] テキスト2つ（positional）か --pairs-file を指定してください")
        sys.exit(1)

    config = Settings()
    print(f"\nモデルをロード中: {config.embedding_model_dir}")
    model = get_embedding_model(model_dir=config.embedding_model_dir)

    print(f"\n類似度比較 ({len(pairs)} ペア, threshold={args.threshold})\n")
    sims = []
    for a, b in pairs:
        sim = compare(a, b, model, args.threshold)
        sims.append(sim)

    if len(sims) > 1:
        print(f"--- 統計 ---")
        print(f"  平均: {np.mean(sims):.4f}")
        print(f"  最大: {np.max(sims):.4f}")
        print(f"  最小: {np.min(sims):.4f}")
        hit_count = sum(1 for s in sims if s >= args.threshold)
        print(f"  閾値以上: {hit_count}/{len(sims)} 件")


if __name__ == "__main__":
    main()
