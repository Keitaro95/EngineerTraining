"""
Presidio日本語PII検出のサンプル実行スクリプト

CSVファイルからテストデータを読み込んで検証します。

## 前処理の特徴

このスクリプトでは、Presidioでの検出精度を向上させるため、
以下の前処理を実施します：

1. **ひらがな・カタカナ数字 → 半角数字変換**
   - 2個以上連続する数字トークンのみ変換
   - 例: "ゼロキューゼロ いちにさんよん" → "090 1234"
   - 孤立した数字トークン（「ご連絡」など）は変換しない

2. **全角数字 → 半角数字変換**
   - NFKC正規化により自動変換
   - 例: "０３−１２３４" → "03-1234"

3. **漢数字 → 半角数字変換**
   - 基本数字のみ（一二三 → 123）
   - 例: "口座番号は普通一二三四五六七" → "口座番号は普通1234567"

これにより、Ginzaを使わずに正規表現のみで高精度な数字正規化を実現します。
"""

import csv
import re
import unicodedata
from pathlib import Path
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Transformer モデルを使う場合は必須
import spacy_curated_transformers  # noqa: F401

from recognizers.japanese_standard import get_all_japanese_recognizers


# ========================================
# テキスト正規化処理
# ========================================

# ひらがな数字の辞書マッピング
KANA_NUMBER_MAP = {
    "きゅう": "9",
    "しち": "7",
    "なな": "7",
    "はち": "8",
    "ぜろ": "0",
    "れい": "0",
    "いち": "1",
    "ろく": "6",
    "よん": "4",
    "さん": "3",
    "ご": "5",
    "く": "9",
    "し": "4",
    "に": "2",
}

# カタカナ数字の辞書マッピング
KATAKANA_NUMBER_MAP = {
    "キュー": "9",
    "キュウ": "9",
    "シチ": "7",
    "ナナ": "7",
    "ハチ": "8",
    "ゼロ": "0",
    "レイ": "0",
    "イチ": "1",
    "ロク": "6",
    "ヨン": "4",
    "サン": "3",
    "ゴ": "5",
    "ク": "9",
    "シ": "4",
    "ニ": "2",
}

# 漢数字の辞書マッピング
KANJI_NUMBER_MAP = {
    "〇": "0",
    "零": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "壱": "1",
    "弐": "2",
    "参": "3",
}


def normalize_kana_numbers(text: str) -> str:
    """
    ひらがな・カタカナ数字が2個以上連続する塊を半角数字に変換する。
    孤立した数字トークン（1個だけ）は変換しない。

    例:
    - "ゼロキューゼロ いちにさんよん" → "090 1234"
    - "ご連絡ください" → "ご連絡ください" (孤立した「ご」は変換しない)
    """
    # 全ての数字トークンを結合してパターンを作成
    all_kana_map = {**KANA_NUMBER_MAP, **KATAKANA_NUMBER_MAP}
    tokens_sorted = sorted(all_kana_map.keys(), key=len, reverse=True)

    # 単一トークンにマッチするパターン
    token_pattern = "|".join(re.escape(t) for t in tokens_sorted)

    # 数字トークンまたは数字・ハイフン・記号を含む連続した文字列を「単語」として抽出
    word_pattern = re.compile(rf"(?:{token_pattern}|[\d\-－ー])+")

    def convert_word(match: re.Match) -> str:
        """単語内で2個以上の数字トークンが連続している場合のみ変換"""
        word = match.group()

        # この単語内の数字トークンの塊（2個以上連続）を検出して変換
        block_pattern = re.compile(rf"(?:{token_pattern})(?:{token_pattern})+")
        single_token_pattern = re.compile(token_pattern)

        def convert_block(block_match: re.Match) -> str:
            block = block_match.group()
            return single_token_pattern.sub(lambda m: all_kana_map[m.group()], block)

        return block_pattern.sub(convert_block, word)

    # 単語単位で処理
    text = word_pattern.sub(convert_word, text)
    return text


def normalize_kanji_numbers(text: str) -> str:
    """
    漢数字（基本数字のみ）を半角数字に直接変換する。

    例:
    - "一二三" → "123"
    - "〇九〇" → "090"
    """
    for kanji, digit in KANJI_NUMBER_MAP.items():
        text = text.replace(kanji, digit)
    return text


def normalize_japanese_text(text: str) -> str:
    """
    日本語テキストを正規化してPresidioに渡す前処理。

    処理順序:
    1. NFKC正規化（全角→半角）
    2. ひらがな数字 → 半角数字（いち→1）
    3. 残った基本漢数字 → 半角数字（一二三→123）

    Args:
        text: 入力テキスト

    Returns:
        正規化されたテキスト

    Example:
        >>> normalize_japanese_text("電話は〇九〇-いちにさん-よんごろく")
        '電話は090-123-456'
    """
    # 1. NFKC正規化（全角英数字・記号→半角）
    text = unicodedata.normalize("NFKC", text)

    # 2. ひらがな・カタカナ数字 → 半角数字
    text = normalize_kana_numbers(text)

    # 3. 残った基本漢数字 → 半角数字
    text = normalize_kanji_numbers(text)

    return text


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
        "CREDIT_CARD_CVV": OperatorConfig("replace", {"new_value": "***"}),
    }

    # 全件処理してマスキング結果を収集
    print("4. PII検出とマスキング処理を実行中...")
    print("-" * 100)

    results_data = []
    total_detected = 0
    entity_stats = {}

    for i, text in enumerate(texts, 1):
        # テキスト正規化（ひらがな数字→半角数字、全角数字→半角数字、漢数字→半角数字）
        text_normalized = normalize_japanese_text(text)

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

    # 結果をCSVに出力（マスキング後のテキストのみ）
    output_path = "output.csv"
    print(f"6. 結果をCSVに出力中: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for data in results_data:
            writer.writerow([data["masked"]])

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
