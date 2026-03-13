"""
フラット化（_flatten_json）確認スクリプト

パーサーが出力した PIR JSON を _flatten_json に通した結果を可視化する。
「どのノードが何チャンクになるか」「チャンクIDとメタデータの内容」を確認できる。
RAGインデックスの中身を理解するための基礎調査用。

使用例:
    cd Lightz-System1/backend
    # PIR JSON を渡して全チャンクを表示
    uv run python ../../factors/構造化use/inspect_flatten.py \
        --pir path/to/pir.json

    # ステップ記号でフィルタ
    uv run python ../../factors/構造化use/inspect_flatten.py \
        --pir path/to/pir.json --step "3.1"

    # チャンク数だけ確認（--summary）
    uv run python ../../factors/構造化use/inspect_flatten.py \
        --pir path/to/pir.json --summary
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Lightz-System1" / "backend"))

from refactored.rag.vector_store import RAGVectorStore
from refactored.config.settings import Settings


def main():
    parser = argparse.ArgumentParser(description="フラット化チャンク確認")
    parser.add_argument("--pir", required=True, help="PIR JSONファイルのパス")
    parser.add_argument("--step", help="手順記号でフィルタ（例: '3.1'）")
    parser.add_argument("--summary", action="store_true", help="チャンク数の集計だけ表示")
    parser.add_argument("--top", type=int, default=50, help="表示件数上限（デフォルト: 50）")
    args = parser.parse_args()

    pir_path = Path(args.pir)
    if not pir_path.exists():
        print(f"[ERROR] PIRファイルが見つかりません: {pir_path}")
        sys.exit(1)

    with open(pir_path, encoding="utf-8") as f:
        pir_json = json.load(f)

    config = Settings()

    # _flatten_json の実行（build_index を呼ばずに df だけ取得）
    vector_store = RAGVectorStore(model_dir=config.embedding_model_dir)
    df = vector_store._flatten_json(pir_json, doc_id=pir_path.stem)

    print(f"\nPIR: {pir_path.name}")
    print(f"総チャンク数: {len(df)}\n")

    if args.summary:
        # ステップ単位のチャンク数集計
        step_counts = df.apply(lambda r: r["meta"]["step"], axis=1).value_counts().sort_index()
        print("ステップ別チャンク数:")
        for step, count in step_counts.items():
            print(f"  {step:10s}: {count} チャンク")

        # type 別集計
        type_counts = df.apply(lambda r: r["meta"].get("type", ""), axis=1).value_counts()
        print("\ntype 別チャンク数:")
        for t, count in type_counts.items():
            label = t if t else "(なし)"
            print(f"  {label:15s}: {count} チャンク")
        return

    # フィルタ
    if args.step:
        df = df[df.apply(lambda r: r["meta"]["step"] == args.step, axis=1)]
        print(f"step='{args.step}' のチャンク数: {len(df)}\n")

    # チャンク一覧表示
    print(f"チャンク一覧（上位 {args.top} 件）\n")
    for i, (_, row) in enumerate(df.head(args.top).iterrows()):
        meta = row["meta"]
        print(f"  [{i+1:3d}] id   : {meta['id']}")
        print(f"        text : {row['text'][:80]}")
        print(f"        step : {meta.get('step', '-')}")
        print(f"        path : {meta.get('path', '-')}")
        print(f"        type : {meta.get('type', '-') or '(なし)'}")
        print(f"        line : {meta.get('line', '-')}")

        # node_json のキー一覧（node全体の構造確認用）
        node_json = meta.get("node_json")
        if node_json:
            node = json.loads(node_json)
            sub_count = len(node.get("sub_steps", []))
            content_count = len(node.get("作業内容", []))
            print(f"        node : keys={list(node.keys())}  作業内容={content_count}行  sub_steps={sub_count}件")
        print()

    if len(df) > args.top:
        print(f"  ... 残り {len(df) - args.top} 件 (--top で件数を変更)")


if __name__ == "__main__":
    main()
