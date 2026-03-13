"""
検索パイプライン実行スクリプト

ルールベース検索（4戦略）→ 最頻出候補選出 → スコア集計の一連を
PIR DataFrame と検索パラメータを渡して単体実行する。
「どの戦略でどのPIRがヒットしたか」「フィルタ後の候補ランキング」を確認できる。

前提:
    pir_df は本来 SQLite DB から取得するが、
    このスクリプトでは CSV ファイルから読み込むことも可能。

使用例:
    cd Lightz-System1/backend
    # CSVから pir_df を読んでキーワード検索を実行
    uv run python ../../factors/構造化use/run_search_pipeline.py \
        --pir-csv path/to/pir_records.csv \
        --keywords "ボルト取付" "トルク確認" \
        --to-number "27-31-00" \
        --triple-sn "00-50-50"

    # IRANサーチ番号で絞り込む
    uv run python ../../factors/構造化use/run_search_pipeline.py \
        --pir-csv path/to/pir_records.csv \
        --iran "*2740-06-04" "*2740-07-08"
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Lightz-System1" / "backend"))

from refactored.search.engine import SearchEngine
from refactored.config.settings import Settings


def print_results(results: dict):
    total = sum(len(v) for v in results.values())
    print(f"\n検索結果 合計: {total} 件\n")

    for strategy, hits in results.items():
        if not hits:
            continue
        print(f"  [{strategy}] {len(hits)} 件")
        for h in hits[:5]:
            print(f"    score={h.score:.4f}  file={h.pir_file_name}")
        if len(hits) > 5:
            print(f"    ... 残り {len(hits) - 5} 件")
        print()


def main():
    parser = argparse.ArgumentParser(description="検索パイプライン実行")
    parser.add_argument("--pir-csv", required=True, help="pir_df CSVファイルのパス")
    parser.add_argument("--keywords", nargs="+", default=[], help="キーワードリスト")
    parser.add_argument("--iran", nargs="+", default=[], help="IRAN検索番号リスト（例: *2740-06-04）")
    parser.add_argument("--to-number", default=None, help="TO番号（例: 27-31-00）")
    parser.add_argument("--triple-sn", default=None, help="トリプルSN（例: 00-50-50）")
    parser.add_argument("--part-numbers", nargs="+", default=[], help="部品番号リスト")
    args = parser.parse_args()

    csv_path = Path(args.pir_csv)
    if not csv_path.exists():
        print(f"[ERROR] CSVファイルが見つかりません: {csv_path}")
        sys.exit(1)

    pir_df = pd.read_csv(csv_path)
    print(f"\nPIR DataFrame: {len(pir_df)} 行  カラム: {list(pir_df.columns)}")

    config = Settings()
    engine = SearchEngine(config)

    print("\n--- 検索実行 ---")
    print(f"  IRAN番号   : {args.iran or '(なし)'}")
    print(f"  TO番号     : {args.to_number or '(なし)'}")
    print(f"  トリプルSN : {args.triple_sn or '(なし)'}")
    print(f"  キーワード : {args.keywords or '(なし)'}")
    print(f"  部品番号   : {args.part_numbers or '(なし)'}")

    # search/engine.py:48-132 の 4戦略実行
    results = engine.search(
        pir_df=pir_df,
        iran_search_numbers=args.iran or None,
        to_number=args.to_number,
        triple_sn=args.triple_sn,
        keywords=args.keywords or None,
        part_numbers=args.part_numbers or None,
    )

    print_results(results)

    # search/filter.py:22-69 最頻出候補選出
    frequent_pairs = engine.get_most_frequent(results)
    print(f"最頻出候補: {len(frequent_pairs)} 件")
    for fname, fhits in frequent_pairs:
        print(f"  {fname}  ({len(fhits)} 戦略でヒット)")

    # search/filter.py:71-105 スコア集計
    aggregated = engine.aggregate_results(results)
    print(f"\nスコア集計ランキング（上位10件）:")
    for agg in aggregated[:10]:
        print(f"  rank={agg.rank}  score={agg.total_score:.4f}  file={agg.pir_file_name}")


if __name__ == "__main__":
    main()
