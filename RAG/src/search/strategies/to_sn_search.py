"""
search/strategies/to_sn_search.py — TO番号/トリプルSN検索（キーワードプルーニング付き）
=======================================================================================
ソース: search/strategies/to_sn_search.py

概要:
  TO番号とトリプルSNをそれぞれ独立して部分一致検索し、
  複数ヒット時はキーワードを使ったプルーニングで絞り込む。

  TO結果とSN結果は別々のリストで返し、engine.py 側で "to"/"sn" として管理する。

精度上のポイント:
  - プルーニングは `any(kw in text for kw in keywords)` — 1語でも含めば通過
  - 絞り込み結果ゼロの場合は元の全結果をそのまま返す（フォールバック）
  - TO番号とSN番号が同一手順書に共存する場合は両方のリストに入る（重複あり）
"""

from typing import List, Optional, Tuple
import pandas as pd


def to_sn_strategy_search(
    pir_df: pd.DataFrame,
    to_number: Optional[str] = None,
    triple_sn: Optional[str] = None,
    keywords: Optional[List[str]] = None,
) -> Tuple[list, list]:
    """
    TO番号とトリプルSNで手順書を検索する。

    Args:
        pir_df    : PIR手順書のDataFrame
        to_number : TO番号（例: "DOC 123456"）
        triple_sn : トリプルSN（例: "00-50-50"）
        keywords  : プルーニング用キーワードリスト

    Returns:
        (to_results, sn_results) のタプル。各要素は SearchResult のリスト。
    """
    # search/strategies/to_sn_search.py:41-73
    to_results = []
    sn_results = []

    for _, row in pir_df.iterrows():
        text = str(row.get("text", ""))

        if to_number and to_number in text:
            to_results.append(_create_result(row, "TO_NUMBER", 1.0, to_number))

        if triple_sn and triple_sn in text:
            sn_results.append(_create_result(row, "TRIPLE_SN", 1.0, triple_sn))

    # プルーニング: 複数ヒット時のみキーワードで絞り込む
    # search/strategies/to_sn_search.py:65-69
    if keywords:
        if len(to_results) > 1:
            to_results = _prune_by_keywords(to_results, keywords)
        if len(sn_results) > 1:
            sn_results = _prune_by_keywords(sn_results, keywords)

    return to_results, sn_results


def _prune_by_keywords(results: list, keywords: List[str]) -> list:
    """
    キーワードを1つでも含む結果に絞り込む。

    絞り込み後が空の場合は元のリストを返す（精度より再現率を優先）。

    search/strategies/to_sn_search.py:77-99
    """
    pruned = [
        r for r in results
        if any(kw in r["metadata"]["text"] for kw in keywords)
    ]
    return pruned if pruned else results  # ゼロなら元に戻す


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
