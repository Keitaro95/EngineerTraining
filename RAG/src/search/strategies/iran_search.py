"""
search/strategies/iran_search.py — IRAN番号検索（最優先・即リターン）
======================================================================
ソース: search/strategies/iran_search.py

概要:
  IRAN番号を pir_df の "text" 列に対して文字列包含で検索する。
  最初のヒットで即座にリターンし、SearchEngine の後続戦略を全てスキップさせる
  「フェイルファスト」パターンの検索戦略。

精度上のポイント:
  - 完全一致ではなく部分一致（`iran_no in text`）
  - 最初の1件ヒットで即リターンするため、複数手順書にまたがる場合は先着優先
  - IRAN番号のフォーマットゆらぎ（スペース有無 等）には対応していない
"""

from typing import List
import pandas as pd


def iran_strategy_search(
    pir_df: pd.DataFrame,
    iran_search_numbers: List[str],
) -> list:
    """
    IRAN番号で手順書を検索する。

    Args:
        pir_df             : PIR手順書のDataFrame（"text", "file_name" カラムを持つ）
        iran_search_numbers: IRAN検索番号リスト（例: ["*70-27-1-2", "*70-27-1-3"]）

    Returns:
        ヒットした SearchResult のリスト。
        最初の1件ヒット時点で return するため、通常は長さ1のリスト。
    """
    # search/strategies/iran_search.py:39-57
    results = []

    for iran_no in iran_search_numbers:
        for _, row in pir_df.iterrows():
            text = str(row.get("text", ""))

            if iran_no in text:                       # 部分一致
                result = _create_result(
                    row=row,
                    search_type="IRAN",
                    score=1.0,
                    matched_text=iran_no,
                )
                results.append(result)
                return results                         # ヒットで即リターン

    return results  # 全番号でヒットなし → []


# ---- IRAN検索番号の生成ロジック（workflow.py:319 より） ----
# iran_search_numbers はこの手順で組み立てられる:
#
#   iran_no   = extracted_data["iran_number"]     # 例: "70-27-1-2"
#   system_no = extracted_data["system_number"]   # 例: "S"
#   step_sym  = extracted_data["step_symbol"]     # 例: "2"
#
#   candidates = [
#       f"*{iran_no}",              # "*70-27-1-2"
#       f"*{iran_no}-{system_no}",  # "*70-27-1-2-S"
#       f"*{iran_no}-{step_sym}",   # "*70-27-1-2-2"
#   ]
#   iran_search_numbers = [c for c in candidates if c != "*"]


# ---- ユーティリティ（base.py:40-70 より） ----

def _create_result(row: pd.Series, search_type: str, score: float, matched_text: str) -> dict:
    """SearchResult 相当の辞書を生成（スタンドアロン用簡易版）"""
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
