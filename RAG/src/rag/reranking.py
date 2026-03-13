"""
rag/reranking.py — 構造フィルタリング（リランキング）
=====================================================
ソース: diff/sentence_diff.py:417-491, search/filter.py:71-105
  - search/filter.py:71-105        (aggregate_by_file)

概要:
  ベクトル検索の後段で構造的スコアによる再ランキングを実施。

  total_score = context_similarity × 0.6 + keyword_overlap × 0.4
    - context_similarity : コサイン類似度ベース（JSON構造の意味的類似）
    - keyword_overlap    : Jaccard係数ベース（用語の重なり）

  閾値（デフォルト 0.5）未満の候補を除外し、残りをスコア降順に返す。
  最後に filter.py がファイル単位でスコアを合算してランク付けする。
"""


# ---- diff/sentence_diff.py:417-491: 構造フィルタリング ----

def filter_hits_by_structure(
    target_dicts: list[dict],
    hits: list[tuple[str, dict]],
    compare_fn,                    # SentenceDiffAnalyzer.compare_jsons_from_df に相当
    threshold: float = 0.5,
    weight_context: float = 0.6,
    weight_keywords: float = 0.4,
) -> list[tuple[str, dict]]:
    """
    ヒット候補を構造スコアでフィルタし、スコア降順に返す。

    diff/sentence_diff.py:417-491 の filter_hits_by_structure() をスタンドアロン化。

    Args:
        target_dicts   : 比較元の構造JSON リスト
        hits           : [(file_name, row_dict), ...] — row["data"] に構造データが必要
        compare_fn     : (target_dict, candidates_df, threshold, w_ctx, w_kw) → DataFrame
        threshold      : 採用閾値（デフォルト 0.5）
        weight_context : コサイン類似度の重み（0.6）
        weight_keywords: Jaccard係数の重み（0.4）

    Returns:
        閾値以上の候補のみをスコア降順で返す
    """
    import pandas as pd

    if not hits or not target_dicts:
        return hits

    df_rows = [
        {"file_name": name, "data": row.get("data"), "text": row.get("text"), "_row": row}
        for name, row in hits
        if row.get("data") is not None
    ]
    if not df_rows:
        return hits

    candidates_df = pd.DataFrame(df_rows)
    best_scores: dict[str, dict] = {}

    for target_dict in target_dicts:
        if target_dict is None:
            continue
        comp_df = compare_fn(target_dict, candidates_df, threshold, weight_context, weight_keywords)
        for _, comp_row in comp_df.iterrows():
            name  = comp_row.get("file_name")
            score = comp_row.get("total_score", 0)
            if name is None or score < threshold:
                continue
            if name not in best_scores or score > best_scores[name].get("total_score", 0):
                best_scores[name] = comp_row.to_dict()

    filtered: list[tuple[str, dict]] = []
    for name, row in hits:
        best = best_scores.get(name)
        if not best:
            continue
        enriched = row.copy()
        enriched["structure_score"]              = best.get("total_score")
        enriched["structure_context_similarity"] = best.get("context_similarity")
        enriched["structure_keyword_overlap"]    = best.get("keyword_overlap")
        filtered.append((name, enriched))

    filtered.sort(key=lambda item: item[1].get("structure_score", 0), reverse=True)
    return filtered


# ---- search/filter.py:71-105: ファイル単位スコア集約 ----

def aggregate_by_file(results: list) -> list:
    """
    SearchResult リストをファイル名で集約し、スコア合計でランク付け。
    search/filter.py:71-105 の aggregate_by_file() に対応。

    Returns:
        AggregatedSearchResult 相当のリスト（スコア降順・rank付き）
    """
    file_map: dict[str, list] = {}
    for r in results:
        file_map.setdefault(r.pir_file_name, []).append(r)

    aggregated = [
        {
            "pir_file_name": fname,
            "total_score"  : sum(r.score for r in file_results),
            "search_results": file_results,
        }
        for fname, file_results in file_map.items()
    ]
    aggregated.sort(key=lambda x: x["total_score"], reverse=True)

    for rank, agg in enumerate(aggregated, start=1):
        agg["rank"] = rank

    return aggregated


# ---- スコア計算式のまとめ ----
# total_score = context_similarity * 0.6 + keyword_overlap * 0.4
#
# context_similarity : コサイン類似度（構造JSON のベクトル距離）
# keyword_overlap    : Jaccard係数
#   = |A ∩ B| / |A ∪ B|   (A=target用語集合, B=候補用語集合)
