"""
search/filter_aggregate.py — 集約・フィルタ（最頻出 / スコアランキング）
=========================================================================
ソース: search/filter.py, search/engine.py:135-180
  - search/engine.py:135-180

概要:
  4戦略から返ってきた Dict[str, List[SearchResult]] を受け取り、
  2種類の集約方式でランキングを生成する。

  方式A — get_most_frequent():
    ファイル名の出現回数（複数戦略でのヒット数）が最大のファイルを選ぶ。
    同率1位は全員選出。

  方式B — aggregate_results():
    ファイル単位でスコアを合算し、合計スコア降順でランク付けする。
    TO/SN/IRAN は固定1.0、キーワードは可変スコアなので合計に差が出る。
"""

from typing import Dict, List, Tuple
from collections import Counter


# ---- 方式A: get_most_frequent ----
# search/filter.py:22-69 / search/engine.py:135-156

def get_most_frequent(
    all_results: Dict[str, list]
) -> List[Tuple[str, list]]:
    """
    全戦略の結果から最頻出ファイルを抽出する。

    Args:
        all_results: {"iran": [...], "to": [...], "sn": [...], "keyword": [...], "part": [...]}

    Returns:
        [(file_name, [SearchResult, ...]), ...] — 最頻出グループ
    """
    combined = []
    for result_list in all_results.values():
        combined.extend(result_list)

    if not combined:
        return []

    # ファイル名の出現回数をカウント（複数戦略でヒット = 高カウント）
    name_counts = Counter(r["pir_file_name"] for r in combined)
    max_count = max(name_counts.values())

    top_names = {name for name, cnt in name_counts.items() if cnt == max_count}

    name_to_results: Dict[str, list] = {}
    for r in combined:
        if r["pir_file_name"] in top_names:
            name_to_results.setdefault(r["pir_file_name"], []).append(r)

    return list(name_to_results.items())


# ---- 方式B: aggregate_results ----
# search/filter.py:71-105 / search/engine.py:158-180

def aggregate_results(
    all_results: Dict[str, list]
) -> List[dict]:
    """
    ファイル単位でスコアを合算し、降順ランキングを付けて返す。

    Args:
        all_results: 戦略別結果辞書

    Returns:
        [
            {
                "rank"          : 1,
                "pir_file_name" : "PIR_001.xlsx",
                "total_score"   : 3.82,
                "search_results": [SearchResult, ...],
            },
            ...
        ]  スコア降順
    """
    combined = []
    for result_list in all_results.values():
        combined.extend(result_list)

    if not combined:
        return []

    file_to_results: Dict[str, list] = {}
    for r in combined:
        file_to_results.setdefault(r["pir_file_name"], []).append(r)

    aggregated = []
    for file_name, file_results in file_to_results.items():
        aggregated.append({
            "pir_file_name":  file_name,
            "total_score":    sum(r["score"] for r in file_results),
            "search_results": file_results,
        })

    aggregated.sort(key=lambda x: x["total_score"], reverse=True)
    for rank, agg in enumerate(aggregated, start=1):
        agg["rank"] = rank

    return aggregated


# ---- その他のフィルタ（search/filter.py より） ----

def filter_by_score(results: list, min_score: float) -> list:
    """スコア閾値でフィルタリング"""
    return [r for r in results if r["score"] >= min_score]


def deduplicate(results: list) -> list:
    """ファイル名ベースで重複を除去（先着優先）"""
    seen = set()
    unique = []
    for r in results:
        if r["pir_file_name"] not in seen:
            seen.add(r["pir_file_name"])
            unique.append(r)
    return unique


def top_n(results: list, n: int) -> list:
    """上位N件を返す"""
    return results[:n]


# ---- 使用例 ----
if __name__ == "__main__":
    # 3戦略でヒットしたファイルが最頻出になる例
    dummy_results = {
        "iran": [],
        "to":      [{"pir_file_name": "A.xlsx", "score": 1.0, "search_type": "TO_NUMBER"}],
        "sn":      [{"pir_file_name": "A.xlsx", "score": 1.0, "search_type": "TRIPLE_SN"},
                    {"pir_file_name": "B.xlsx", "score": 1.0, "search_type": "TRIPLE_SN"}],
        "keyword": [{"pir_file_name": "A.xlsx", "score": 0.42, "search_type": "KEYWORD"},
                    {"pir_file_name": "B.xlsx", "score": 0.61, "search_type": "KEYWORD"}],
        "part":    [],
    }

    print("=== get_most_frequent ===")
    for name, items in get_most_frequent(dummy_results):
        print(f"  {name}: {len(items)}件ヒット")

    print("\n=== aggregate_results ===")
    for agg in aggregate_results(dummy_results):
        print(f"  rank={agg['rank']} {agg['pir_file_name']} total={agg['total_score']:.2f}")
