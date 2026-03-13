"""
search/strategies/part_search.py — 部品番号検索（行単位・先着ブレイク）
========================================================================
ソース: search/strategies/part_search.py

概要:
  部品番号リストを pir_df の各行に対して順番にチェックし、
  最初にヒットした部品番号でその行を登録して次の行へ進む。
  同一行に複数の部品番号がマッチしても重複登録しない設計。

  スコアは固定 1.0（定性的なヒット）。

精度上のポイント:
  - 部品番号は `part_no in text` の部分一致
  - 部品番号リストの順序によって "どの番号でヒット扱いになるか" が変わる
  - part_numbers はトリプルSNと重複する番号を事前に除外済み（workflow.py 側）
"""

from typing import List
import pandas as pd


def part_strategy_search(
    pir_df: pd.DataFrame,
    part_numbers: List[str],
) -> list:
    """
    部品番号で手順書を検索する。

    Args:
        pir_df       : PIR手順書のDataFrame
        part_numbers : 部品番号リスト（トリプルSNとの重複除外済み）

    Returns:
        SearchResult のリスト。1行につき最大1件。
    """
    # search/strategies/part_search.py:39-58
    results = []

    for _, row in pir_df.iterrows():
        text = str(row.get("text", ""))

        for part_no in part_numbers:
            if part_no in text:
                result = _create_result(row, "PART_NUMBER", 1.0, part_no)
                results.append(result)
                break  # この行は登録済み → 次の行へ（重複防止）

    return results


# ---- 部品番号リストの前処理（workflow.py 側のロジック概要） ----
#
# LLM が抽出した部品番号候補から triple_sn と重複するものを除外する:
#
#   raw_parts  = llm_output["part_numbers"]   # 例: ["00-50-50", "MS12345", "AS67890"]
#   triple_sn  = parsed_to["triple_sn"]       # 例: "00-50-50"
#   part_numbers = [p for p in raw_parts if p != triple_sn]
#   # → ["MS12345", "AS67890"]


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
