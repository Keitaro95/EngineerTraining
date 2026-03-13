"""
rag/vector_search.py — RAGベクトル検索（同義語展開 + 重複排除）
================================================================
ソース: rag/vector_store.py:148-254
概要:
  1. クエリを同義語ペアで正規化し、さらに同義語バリアントを生成
  2. 全バリアントを一括エンコードして ChromaDB へクエリ
  3. チャンクID単位で重複排除（同IDの最高スコアのみ保持）
  4. search_node() で閾値 0.80 判定し、below_threshold フラグを付与
"""

from typing import Optional


def build_query_variants(
    query: str,
    pair_words: list[tuple[str, list[str]]],
) -> list[str]:
    """
    クエリを同義語で正規化し、さらに同義語バリアントを生成。

    rag/vector_store.py:149-166 に対応。

    Args:
        query     : 元クエリ
        pair_words: [(標準語, [類義語, ...]), ...]

    Returns:
        重複なしのクエリ変種リスト
    """
    # Step1: 類義語 → 標準語に置換（正規化）
    normalized = query
    for kw, sim_words in pair_words:
        for sim_word in sim_words:
            if sim_word in normalized:
                normalized = normalized.replace(sim_word, kw)

    variants: set[str] = {normalized}

    # Step2: 標準語 → 類義語 に置換したバリアントを追加
    for kw, sim_words in pair_words:
        if kw and kw in normalized:
            for sim_word in sim_words:
                variants.add(normalized.replace(kw, sim_word))

    return list(variants)


def aggregate_search_results(
    variant_list: list[str],
    raw_results: dict,  # ChromaDB query() の戻り値
) -> list[dict]:
    """
    複数クエリバリアントの結果をチャンクID単位で集約（最高スコア保持）。

    rag/vector_store.py:179-203 に対応。

    Args:
        variant_list : クエリバリアントリスト
        raw_results  : collection.query() の戻り値

    Returns:
        スコア降順の検索結果リスト
    """
    aggregated: dict[str, dict] = {}

    for idx, variant in enumerate(variant_list):
        ids    = raw_results["ids"][idx]
        docs   = raw_results["documents"][idx]
        metas  = raw_results["metadatas"][idx]
        scores = raw_results["distances"][idx]

        for doc_id, doc_text, meta, dist in zip(ids, docs, metas, scores):
            similarity = 1 - dist  # ChromaDB はL2距離を返す

            if doc_id not in aggregated or aggregated[doc_id]["similarity"] < similarity:
                aggregated[doc_id] = {
                    "id"        : doc_id,
                    "text"      : doc_text,
                    "meta"      : meta,
                    "similarity": similarity,
                    "query"     : variant,
                }

    hits = sorted(aggregated.values(), key=lambda x: x["similarity"], reverse=True)
    return hits


def search_node(
    collection,
    embedding_model,
    query: str,
    pair_words: Optional[list] = None,
    top_k: int = 3,
    threshold: float = 0.80,
) -> Optional[dict]:
    """
    ノード検索。閾値未満のヒットは below_threshold=True フラグを付与して返す。

    rag/vector_store.py:206-254 に対応。

    Returns:
        {node, path, line, step, type, text, similarity, below_threshold}
        ヒットなしの場合 None
    """
    import json

    pair_words = pair_words or []
    variant_list = build_query_variants(query, pair_words)

    query_emb = embedding_model.encode(variant_list, normalize_embeddings=True, show_progress_bar=False)
    raw_results = collection.query(query_embeddings=query_emb.tolist(), n_results=top_k)

    hits = aggregate_search_results(variant_list, raw_results)
    if not hits:
        return None

    hit  = hits[0]
    meta = hit["meta"]
    path = meta["path"].split("/") if isinstance(meta["path"], str) else meta["path"]
    node = json.loads(meta["node_json"]) if meta.get("node_json") else None

    return {
        "node"            : node,
        "path"            : path,
        "line"            : meta["line"],
        "step"            : meta["step"],
        "type"            : meta["type"],
        "text"            : hit["text"],
        "similarity"      : hit["similarity"],
        "below_threshold" : hit["similarity"] < threshold,
    }
