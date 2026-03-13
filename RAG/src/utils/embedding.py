"""
utils/embedding.py — Embeddingモデル接続（pytorch / ONNX 切替）
================================================================
ソース: rag/embeddings.py:23-312
概要:
  intfloat/multilingual-e5-small を使用。
  PyTorch / ONNX の2バックエンドを環境変数で切替可能なシングルトン設計。
  全ベクトルを L2 正規化 → コサイン類似度をそのまま内積で計算できる。
"""

import os
import numpy as np
from pathlib import Path


# ---- バックエンド選択（rag/embeddings.py:23-48）----
DEFAULT_MODEL_NAME = "intfloat/multilingual-e5-small"

def get_embedding_model(
    model_dir: Path = Path("./models/e5-small"),
    backend: str | None = None,
):
    """
    シングルトンで埋め込みモデルを返す。
    backend=None の場合、環境変数 EMBEDDING_BACKEND を参照（デフォルト: pytorch）。
    """
    if backend is None:
        backend = os.getenv("EMBEDDING_BACKEND", "pytorch").lower()

    if backend == "onnx":
        return _build_onnx_model(model_dir)
    return _build_pytorch_model(model_dir)


# ---- PyTorch バックエンド（rag/embeddings.py:102-162）----
def _build_pytorch_model(model_dir: Path):
    """SentenceTransformer でモデルをロード or ダウンロード後にローカル保存。"""
    from sentence_transformers import SentenceTransformer

    if model_dir.exists():
        model = SentenceTransformer(str(model_dir))
    else:
        model = SentenceTransformer(DEFAULT_MODEL_NAME)
        model_dir.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(model_dir))

    return model  # .encode(texts, normalize_embeddings=True) で使用


# ---- ONNX バックエンド（rag/embeddings.py:165-311）----
def _build_onnx_model(model_dir: Path):
    """optimum でエクスポートした ONNX モデルをロード。初回のみ変換を実行。"""
    from optimum.onnxruntime import ORTModelForFeatureExtraction
    from transformers import AutoTokenizer

    onnx_dir = model_dir.parent / f"{model_dir.name}-onnx"

    if (onnx_dir / "model.onnx").exists():
        tokenizer = AutoTokenizer.from_pretrained(str(onnx_dir))
        model = ORTModelForFeatureExtraction.from_pretrained(
            str(onnx_dir), provider="CPUExecutionProvider"
        )
    else:
        onnx_dir.mkdir(parents=True, exist_ok=True)
        source = str(model_dir) if model_dir.exists() else DEFAULT_MODEL_NAME
        model = ORTModelForFeatureExtraction.from_pretrained(
            source, export=True, provider="CPUExecutionProvider"
        )
        tokenizer = AutoTokenizer.from_pretrained(source)
        model.save_pretrained(str(onnx_dir))
        tokenizer.save_pretrained(str(onnx_dir))

    return tokenizer, model


# ---- Mean Pooling + L2 正規化（rag/embeddings.py:286-311）----
def mean_pooling(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """
    ONNX バックエンド用 mean pooling。
    token_embeddings: (batch, seq_len, hidden)
    attention_mask  : (batch, seq_len)
    """
    mask = np.expand_dims(attention_mask, axis=-1)
    mask = np.broadcast_to(mask, token_embeddings.shape)
    sum_emb  = np.sum(token_embeddings * mask, axis=1)
    sum_mask = np.clip(np.sum(mask, axis=1), a_min=1e-9, a_max=None)
    return sum_emb / sum_mask


def l2_normalize(embeddings: np.ndarray) -> np.ndarray:
    """全ベクトルをL2正規化。コサイン類似度 = 内積で計算可能になる。"""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms
