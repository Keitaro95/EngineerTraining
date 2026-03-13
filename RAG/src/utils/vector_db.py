"""
utils/vector_db.py — ChromaDB 操作（add / query / clear）
==========================================================
ソース: rag/vector_store.py:36-80
概要:
  ChromaDB をインメモリで起動し、ID・テキスト・メタデータ・
  事前計算済み埋め込みをセットで格納する。
  永続化不要なプロトタイプ向け構成（PersistentClient は使わない）。
"""

import chromadb


# ---- 初期化パターン（rag/vector_store.py:36-40）----

def create_vector_store(collection_name: str = "docs"):
    """
    インメモリ ChromaDB クライアントとコレクションを生成。

    Note:
        chromadb.Client() はインメモリのみ。
        PersistentClient は delete_collection が不安定なため避ける。
    """
    client = chromadb.Client()
    collection = client.get_or_create_collection(collection_name)
    return collection


# ---- ドキュメント追加（rag/vector_store.py:44-62）----

def add_chunk(collection, chunk_id: str, text: str, meta: dict, embedding: list) -> None:
    """
    1チャンクをコレクションへ追加。

    Args:
        collection : ChromaDB コレクション
        chunk_id   : {doc_id}:{path}:{line} の形式
        text       : チャンクのテキスト
        meta       : {"doc_id", "path", "line", "step", "type", "node_json"}
        embedding  : 事前計算済みベクトル（L2正規化済み）のリスト
    """
    collection.add(
        ids=[chunk_id],
        documents=[text],
        metadatas=[meta],
        embeddings=[embedding],
    )


# ---- コレクションのクリア（rag/vector_store.py:256-268）----

def clear_collection(collection) -> None:
    """
    コレクション内の全ドキュメントを削除（再構築用）。
    delete_collection ではなく全ID取得→削除で安全にクリア。
    """
    try:
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)
    except Exception:
        pass  # コレクションが空の場合は無視
