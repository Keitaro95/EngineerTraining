"""
utils/keyword_scoring.py — キーワードスコアリング共通ロジック
=============================================================
ソース: search/scorer.py:20-77
概要:
  score = [(coverage + density) / 2] × size_penalty

  - coverage    = ヒットKW数 / 全KW数
  - density     = ヒット文字数合計 / テキスト長
  - size_penalty = log(KW数+1) / log(16)   ← KW数が少ない低確度クエリを抑制

  例: 1語 ≈ 0.25倍, 2語 ≈ 0.40倍, 4語 ≈ 0.58倍, 8語 ≈ 0.77倍
"""

import math


def calc_keyword_score(
    texts: str | list[str],
    keywords: list[str],
) -> tuple[float, list[str]]:
    """
    キーワードスコアを計算する。
    search/scorer.py:20-77 の SearchScorer.calc_keyword_score() をスタンドアロン化。

    Args:
        texts   : 検索対象テキスト（文字列 or リスト）
        keywords: 検索キーワードリスト

    Returns:
        (score: float, matched_keywords: list[str])
    """
    if not keywords:
        return 0.0, []

    # テキストを1文字列に結合
    if isinstance(texts, (list, tuple)):
        text_str = "\n".join(str(t) for t in texts)
    else:
        text_str = str(texts or "")

    # マッチング
    hit_terms = [kw for kw in keywords if kw in text_str]
    if not hit_terms:
        return 0.0, []

    # coverage: ヒットKW数 / 全KW数
    coverage = len(hit_terms) / len(keywords)

    # density: ヒット文字数合計 / テキスト長
    hit_chars = sum(text_str.count(term) * len(term) for term in hit_terms)
    density = hit_chars / max(len(text_str), 1)

    # 基本スコア
    score = (coverage + density) / 2

    # size_penalty: KW数が少ないほどスコアを抑制（log スケール）
    kw_count = max(len(keywords), 1)
    size_penalty = min(1.0, math.log(kw_count + 1) / math.log(16))
    score *= size_penalty

    return score, hit_terms


# ---- 動作確認 ----
if __name__ == "__main__":
    text = "フィルターキャップのパッキングを取り付ける。次に光源を取り外す。"
    kws  = ["フィルターキャップ", "パッキング", "取付"]
    score, hits = calc_keyword_score(text, kws)
    print(f"score={score:.3f}, hits={hits}")
