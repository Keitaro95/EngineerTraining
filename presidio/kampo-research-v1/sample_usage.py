"""
Presidio日本語PII検出のサンプル実行スクリプト

CSVファイルからテストデータを読み込んで検証します。
"""

import csv
import unicodedata
from pathlib import Path
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from recognizers.japanese_standard import get_all_japanese_recognizers


def load_csv_data(csv_path):
    """CSVファイルからテストデータを読み込む"""
    texts = []
    csv_file = Path(csv_path)

    if not csv_file.exists():
        print(f"エラー: CSVファイルが見つかりません: {csv_path}")
        return []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():  # 空行をスキップ
                texts.append(row[0].strip())

    return texts


def main():
    print("=" * 100)
    print("Presidio 日本語PII検出 サンプル実行")
    print("=" * 100)
    print()

    # セットアップ
    print("1. NLPエンジンと日本語モデルをセットアップ中...")
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

    # Recognizerの登録
    print("2. 日本語PII Recognizerを登録中...")
    for recognizer in get_all_japanese_recognizers():
        analyzer.registry.add_recognizer(recognizer)

    print("   セットアップ完了！")
    print()

    # CSVファイルからデータ読み込み
    csv_path = "sample.csv"
    print(f"3. CSVファイルを読み込み中: {csv_path}")
    texts = load_csv_data(csv_path)

    if not texts:
        print("   エラー: テストデータが読み込めませんでした。")
        return

    print(f"   {len(texts)}件のテストデータを読み込みました")
    print()

    # マスキング設定
    anonymizer = AnonymizerEngine()
    operators = {
        "DEFAULT": OperatorConfig("replace", {"new_value": "[MASKED]"}),
        "PERSON": OperatorConfig("replace", {"new_value": "[氏名]"}),
        "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[MASKED]"}),
        "JP_ADDRESS": OperatorConfig("replace", {"new_value": "[住所]"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "[生年月日]"}),
        "JP_MY_NUMBER": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 12, "from_end": False}),
        "JP_BANK_ACCOUNT": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 5, "from_end": False}),
        "CREDIT_CARD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 12, "from_end": False}),
    }

    # 全件処理してマスキング結果を収集
    print("4. PII検出とマスキング処理を実行中...")
    print("-" * 100)

    results_data = []
    total_detected = 0
    entity_stats = {}

    for i, text in enumerate(texts, 1):
        # NFKC正規化
        text_normalized = unicodedata.normalize("NFKC", text)

        # PII検出
        results = analyzer.analyze(text=text_normalized, language="ja")

        # マスキング処理
        if results:
            total_detected += 1
            anonymized_result = anonymizer.anonymize(
                text=text_normalized,
                analyzer_results=results,
                operators=operators
            )
            masked_text = anonymized_result.text

            # 統計情報を収集
            for result in results:
                entity_stats[result.entity_type] = entity_stats.get(result.entity_type, 0) + 1
        else:
            masked_text = text_normalized

        # 結果を保存
        results_data.append({
            "original": text,
            "masked": masked_text,
            "detected_count": len(results)
        })

        # 進捗表示（10件ごと）
        if i % 10 == 0:
            print(f"   処理中... {i}/{len(texts)}")

    print(f"   処理完了: {len(texts)}件")
    print("-" * 100)
    print()

    # 統計サマリー
    print("5. 検出サマリー:")
    print(f"   総テストケース数: {len(texts)}")
    print(f"   PII/SPII検出あり: {total_detected} ({total_detected/len(texts)*100:.1f}%)")
    print()

    if entity_stats:
        print("   エンティティ別検出数:")
        sorted_stats = sorted(entity_stats.items(), key=lambda x: x[1], reverse=True)
        for entity_type, count in sorted_stats:
            print(f"     {entity_type:20}: {count:4}件")
    print()

    # 結果をCSVに出力
    output_path = "output.csv"
    print(f"6. 結果をCSVに出力中: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["元のテキスト", "マスキング後のテキスト"])
        for data in results_data:
            writer.writerow([data["original"], data["masked"]])

    print(f"   {len(results_data)}件の結果を出力しました")
    print()

    print("=" * 100)
    print("サンプル実行完了！")
    print("=" * 100)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print()
        print("spaCyモデルがインストールされていない場合は、以下を実行してください:")
        print("  python -m spacy download ja_core_news_trf")
