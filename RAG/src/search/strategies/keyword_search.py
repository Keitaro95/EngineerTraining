"""
search/strategies/keyword_search.py — キーワード検索（スコアリング）
=====================================================================
ソース: search/strategies/keyword_search.py, search/scorer.py:20-77
  - search/scorer.py:20-77

概要:
  4戦略の中で唯一スコアリングを持つ検索。
  カバレッジ（マッチ率）と密度（文字密度）を平均し、
  キーワード数が少ないほどスコアを抑えるサイズペナルティを乗算する。

スコア計算式:
  coverage      = len(hit_terms) / len(keywords)
  density       = Σ(text.count(kw) * len(kw)) / len(text)
  base_score    = (coverage + density) / 2
  size_penalty  = log(len(keywords) + 1) / log(16)
  final_score   = base_score * size_penalty

ペナルティ例:
  1語 → 0.25倍, 2語 → 0.40倍, 4語 → 0.58倍, 8語 → 0.77倍, 15語 → 1.00倍
"""

import math
from typing import List, Tuple
import pandas as pd


# ---- キーワードスコア計算 ----
# search/scorer.py:20-77

def calc_keyword_score(
    text: str,
    keywords: List[str],
) -> Tuple[float, List[str]]:
    """
    テキストに対するキーワードスコアを計算する。

    Args:
        text    : 検索対象テキスト（1行分）
        keywords: キーワードリスト

    Returns:
        (score, hit_terms)
        score    : 最終スコア（0.0 〜 1.0 程度、超えることもある）
        hit_terms: マッチしたキーワードのリスト
    """
    if not keywords or not text:
        return 0.0, []

    text_str = str(text)

    # マッチング（部分一致）
    hit_terms = [kw for kw in keywords if kw in text_str]

    if not hit_terms:
        return 0.0, []

    # カバレッジ: マッチしたキーワード数 / 全キーワード数
    coverage = len(hit_terms) / len(keywords)

    # 密度: マッチした文字数の合計 / テキスト全体文字数
    hit_chars = sum(text_str.count(kw) * len(kw) for kw in hit_terms)
    density = hit_chars / max(len(text_str), 1)

    # 基本スコア
    score = (coverage + density) / 2

    # サイズペナルティ: キーワード数が少ないほどスコアを抑制
    # log(16) = 4語相当を基準に正規化
    keyword_count = max(len(keywords), 1)
    size_penalty = min(1.0, math.log(keyword_count + 1) / math.log(16))
    score *= size_penalty

    return score, hit_terms


# ---- キーワード検索戦略本体 ----
# search/strategies/keyword_search.py:33-103

MIN_KEYWORD_SCORE = 0.05  # デフォルト閾値（config.settings より）


def keyword_strategy_search(
    pir_df: pd.DataFrame,
    keywords: List[str],
    min_score: float = MIN_KEYWORD_SCORE,
) -> list:
    """
    キーワードスコアが閾値以上の手順書をスコア降順で返す。

    Args:
        pir_df   : PIR手順書のDataFrame
        keywords : キーワードリスト
        min_score: 最小スコア閾値（未満は除外）

    Returns:
        SearchResult のリスト（スコア降順）
    """
    scored = []

    for _, row in pir_df.iterrows():
        text = row.get("text", "")
        score, hit_terms = calc_keyword_score(text, keywords)

        if score < min_score:
            continue

        result = _create_result(row, "KEYWORD", score, ", ".join(hit_terms))
        result["metadata"]["hit_terms"]     = hit_terms
        result["metadata"]["keyword_count"] = len(hit_terms)
        scored.append((score, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]


# ---- ユーティリティ ----

def _create_result(row: pd.Series, search_type: str, score: float, matched_text: str) -> dict:
    return {
        "pir_file_name": row.get("file_name", ""),
        "search_type":   search_type,
        "score":         score,
        "matched_text":  matched_text,
        "metadata": {
            "text": row.get("text", ""),
            "data": row.get("data", {}),
        },
    }


# ---- スコア例 ----
if __name__ == "__main__":
    samples = [
        ("エンジンのオイルを交換する作業手順を確認してください", ["オイル", "エンジン", "交換"]),
        ("ボルトを締め付ける", ["ボルト"]),
        ("燃料ポンプの点検および交換手順", ["燃料ポンプ", "点検", "交換", "手順", "確認"]),
    ]
    for text, kws in samples:
        score, hits = calc_keyword_score(text, kws)
        penalty = min(1.0, math.log(len(kws) + 1) / math.log(16))
        print(f"スコア={score:.3f}  ヒット={hits}  ペナルティ={penalty:.2f}  kw数={len(kws)}")
