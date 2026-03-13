"""
preprocessing/chunking.py — チャンキング（1行1ベクトル）
=========================================================
ソース: rag/vector_store.py:82-126
概要:
  フラット化した各テキスト行を 1チャンク = 1ベクトル として ChromaDB へ登録。
  チャンクIDは {doc_id}:{path}:{line_index} で一意に管理し、
  メタデータ（階層パス・ステップ名・ノード種別）を同時に保持することで
  後段の構造フィルタリングを可能にする。
"""

# ---- rag/vector_store.py:44-80: チャンク登録 & インデックス構築 ----

# 疑似コード（実クラスは RAGVectorStore）
class ChunkIndexer:
    """
    フラット化済みチャンクを埋め込みベクトル付きで格納するミニマル実装例。
    実装は rag/vector_store.py の RAGVectorStore.build_index / add_from_dataframe を参照。
    """

    def add_chunk(self, chunk_id: str, text: str, meta: dict, embedding_model) -> None:
        """
        1チャンクを ChromaDB コレクションへ追加。

        - IDは {doc_id}:{path}:{line_index} の形式（一意性保証）
        - embeddingは事前計算済みをそのまま渡す（normalize_embeddings=True）
        - metaにはパス・ステップ記号・ノード種別・元JSONを保持
        """
        emb = embedding_model.encode([text], normalize_embeddings=True, show_progress_bar=False)
        # collection.add(ids=[chunk_id], documents=[text], metadatas=[meta], embeddings=emb.tolist())

    def build_index(self, flattened_rows: list[dict], doc_id: str, embedding_model) -> None:
        """
        フラット化済み行リストから全チャンクを登録。
        rag/vector_store.py:64-80 の build_index に対応。
        """
        for row in flattened_rows:
            self.add_chunk(
                chunk_id=row["meta"]["id"],
                text=row["text"],
                meta=row["meta"],
                embedding_model=embedding_model,
            )


# ---- チャンクID設計（重要）----
# チャンクIDが一意でないとベクトル検索の重複排除が崩壊する。
# フォーマット: "{doc_id}:{step0/sub0/...}:{line_index}"
# 例:           "PIR-001:step2/sub1:3"
#
# このIDを使い、後段の search() で
#   aggregated[doc_id] の最高スコアだけを保持 (重複排除) する。
