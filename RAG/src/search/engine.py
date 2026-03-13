"""
search/engine.py — SearchEngine（4戦略の統合・優先制御）
=========================================================
ソース: search/engine.py:48-132

概要:
  4つの検索戦略を優先順位付きで順次実行し、
  戦略別に仕切られた結果辞書 Dict[str, List[SearchResult]] を返す。
  IRAN検索がヒットした時点で即リターンし、後続戦略をスキップする。
"""

from typing import List, Dict, Optional
import pandas as pd


def search(
    pir_df: pd.DataFrame,
    iran_search_numbers: Optional[List[str]] = None,
    to_number: Optional[str] = None,
    triple_sn: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    part_numbers: Optional[List[str]] = None,
) -> Dict[str, list]:
    """
    4戦略の複合検索。優先順位: IRAN > TO/SN > キーワード > 部品番号

    Returns:
        {
            "iran":    [],  # IRAN番号検索結果
            "to":      [],  # TO番号検索結果
            "sn":      [],  # トリプルSN検索結果
            "keyword": [],  # キーワード検索結果
            "part":    [],  # 部品番号検索結果
        }
    """
    results = {"iran": [], "to": [], "sn": [], "keyword": [], "part": []}

    # --- [1] IRAN検索（最優先）ヒットしたら即リターン ---
    # search/engine.py:82-93
    if iran_search_numbers:
        iran_results = iran_strategy_search(pir_df, iran_search_numbers)
        if iran_results:
            results["iran"] = iran_results
            return results  # 他の検索はスキップ

    # --- [2] TO/SN検索 ---
    # search/engine.py:96-105
    if to_number or triple_sn:
        to_results, sn_results = to_sn_strategy_search(
            pir_df, to_number, triple_sn, keywords
        )
        results["to"] = to_results
        results["sn"] = sn_results

    # --- [3] キーワード検索 ---
    # search/engine.py:108-114
    if keywords:
        results["keyword"] = keyword_strategy_search(pir_df, keywords)

    # --- [4] 部品番号検索 ---
    # search/engine.py:117-123
    if part_numbers:
        results["part"] = part_strategy_search(pir_df, part_numbers)

    return results


# ---- 集約: get_most_frequent ----
# search/engine.py:135-156

from collections import Counter


def get_most_frequent(all_results: Dict[str, list]) -> list:
    """
    全戦略の結果を統合し、最も多くヒットしたファイル名グループを返す。

    Counter で pir_file_name の出現回数を数え、最大値と同数のファイルを全員選出。
    同率1位が複数ある場合はすべて返す。
    """
    combined = []
    for result_list in all_results.values():
        combined.extend(result_list)

    if not combined:
        return []

    name_counts = Counter(r.pir_file_name for r in combined)
    max_count = max(name_counts.values())
    top_names = {name for name, cnt in name_counts.items() if cnt == max_count}

    name_to_results: Dict[str, list] = {}
    for r in combined:
        if r.pir_file_name in top_names:
            name_to_results.setdefault(r.pir_file_name, []).append(r)

    return list(name_to_results.items())  # [(file_name, [SearchResult, ...]), ...]


# ---- 集約: aggregate_results ----
# search/engine.py:158-180

def aggregate_results(all_results: Dict[str, list]) -> list:
    """
    ファイル単位でスコアを合算し、降順ランキングを付けて返す。

    返り値の各要素は AggregatedSearchResult:
        pir_file_name : str
        total_score   : float  (全戦略のスコア合計)
        rank          : int    (1-indexed)
        search_results: List[SearchResult]
    """
    combined = []
    for result_list in all_results.values():
        combined.extend(result_list)

    if not combined:
        return []

    file_to_results: Dict[str, list] = {}
    for r in combined:
        file_to_results.setdefault(r.pir_file_name, []).append(r)

    aggregated = []
    for file_name, file_results in file_to_results.items():
        aggregated.append({
            "pir_file_name": file_name,
            "total_score":   sum(r.score for r in file_results),
            "search_results": file_results,
        })

    aggregated.sort(key=lambda x: x["total_score"], reverse=True)
    for rank, agg in enumerate(aggregated, start=1):
        agg["rank"] = rank

    return aggregated
