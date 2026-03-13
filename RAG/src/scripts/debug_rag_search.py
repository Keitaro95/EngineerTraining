"""
RAG検索デバッグスクリプト

PIR JSONをインデックス化し、任意クエリで検索結果・スコア・ノード情報を確認する。

使用例:
    cd Lightz-System1/backend
    uv run python ../../factors/構造化use/debug_rag_search.py \
        --pir path/to/pir.json \
        --query "ボルトを取り外す"

    # 閾値・件数を変えて確認
    uv run python ../../factors/構造化use/debug_rag_search.py \
        --pir path/to/pir.json \
        --query "ボルトを取り外す" \
        --threshold 0.75 \
        --top-k 5

    # 類義語ペアを使って検索バリアントを展開
    uv run python ../../factors/構造化use/debug_rag_search.py \
        --pir path/to/pir.json \
        --query "ファスナを取り外す" \
        --pair-words path/to/similar_words.json
"""

import argparse
import json
import sys
from pathlib import Path

# refactored パッケージをインポートできるようにパスを追加
# 実行ディレクトリ: Lightz-System1/backend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Lightz-System1" / "backend"))

from refactored.rag.vector_store import RAGVectorStore
from refactored.rag.indexer import RAGIndexer
from refactored.rag.retriever import RAGRetriever
from refactored.config.settings import Settings


def load_pair_words(path: str) -> list:
    """
    similar_words.json を [(キーワード, [類義語, ...]), ...] 形式に変換。

    JSONフォーマット想定:
        {"ファスナ": ["ボルト", "ねじ"], "取り外す": ["除去する", "脱着する"]}
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [(k, v) for k, v in raw.items()]


def print_hit(index: int, hit: dict, threshold: float):
    sim = hit.get("similarity", 0)
    meta = hit.get("meta", {})
    ok = sim >= threshold
    flag = "✅" if ok else "⚠️ 閾値未満"
    print(f"  [{index}] {flag}  similarity={sim:.4f}")
    print(f"       text : {hit['text']}")
    print(f"       step : {meta.get('step', '-')}")
    print(f"       path : {meta.get('path', '-')}")
    print(f"       type : {meta.get('type', '-')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="RAG検索デバッグ")
    parser.add_argument("--pir", required=True, help="PIR JSONファイルのパス")
    parser.add_argument("--query", required=True, help="検索クエリ文字列")
    parser.add_argument("--threshold", type=float, default=0.80, help="類似度閾値（デフォルト: 0.80）")
    parser.add_argument("--top-k", type=int, default=3, help="取得件数（デフォルト: 3）")
    parser.add_argument("--pair-words", help="類義語JSONファイルのパス（省略可）")
    args = parser.parse_args()

    pir_path = Path(args.pir)
    if not pir_path.exists():
        print(f"[ERROR] PIRファイルが見つかりません: {pir_path}")
        sys.exit(1)

    with open(pir_path, encoding="utf-8") as f:
        pir_json = json.load(f)

    pair_words = []
    if args.pair_words:
        pair_words = load_pair_words(args.pair_words)

    config = Settings()

    # --- インデックス構築 (vector_store.build_index → _flatten_json → add_from_dataframe) ---
    print(f"\n[1] インデックス構築: {pir_path.name}")
    vector_store = RAGVectorStore(model_dir=config.embedding_model_dir)
    indexer = RAGIndexer(vector_store)
    indexer.index_from_json(pir_json, doc_id=pir_path.stem)

    df = vector_store.df
    total = len(df) if df is not None else 0
    print(f"    チャンク数: {total} 件")

    if df is not None and not df.empty:
        print("    チャンクサンプル（先頭3件）:")
        for _, row in df.head(3).iterrows():
            print(f"      id={row['meta']['id']}  text={row['text'][:40]}")

    # --- top-k 検索 (vector_store.search → クエリ変種展開 → 重複排除) ---
    retriever = RAGRetriever(vector_store, default_threshold=args.threshold)

    print(f"\n[2] top-{args.top_k} 検索")
    print(f"    クエリ   : {args.query}")
    print(f"    閾値     : {args.threshold}")
    if pair_words:
        print(f"    類義語   : {len(pair_words)} ペア")
    print()

    results = retriever.retrieve(args.query, pair_words=pair_words, top_k=args.top_k)

    if not results:
        print("    ヒットなし\n")
    else:
        for i, hit in enumerate(results, 1):
            print_hit(i, hit, args.threshold)

    # --- ノード検索 (search_node → node_json復元 → below_thresholdフラグ) ---
    print("[3] search_node（best hit + node 復元）")
    node_result = retriever.retrieve_node(args.query, pair_words=pair_words, threshold=args.threshold)

    if node_result is None:
        print("    ヒットなし\n")
        return

    sim = node_result.get("similarity", 0)
    below = node_result.get("below_threshold", False)
    print(f"    similarity : {sim:.4f} {'← 閾値未満（not adopted）' if below else ''}")
    print(f"    text       : {node_result['text']}")
    print(f"    step       : {node_result.get('step', '-')}")
    print(f"    path       : {node_result.get('path', '-')}")

    node = node_result.get("node")
    if node:
        print(f"    node keys  : {list(node.keys())}")
        sub_steps = node.get("sub_steps", [])
        if sub_steps:
            print(f"    sub_steps  : {len(sub_steps)} 件")


if __name__ == "__main__":
    main()
