"""
日本語PII検出のテストスクリプト

code-document.mdに記載された8つのPII項目を検証するテストケース。
実行方法: python test_recognizers.py
"""

import unicodedata
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from recognizers.japanese_standard import get_all_japanese_recognizers


def setup_analyzer():
    """日本語対応のAnalyzerEngineをセットアップ"""
    # ① NLPエンジンに日本語モデルを設定
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

    # 日本語標準PII Recognizerを登録
    for recognizer in get_all_japanese_recognizers():
        analyzer.registry.add_recognizer(recognizer)

    return analyzer


def test_pii_detection(analyzer):
    """各PII項目のテストケース"""

    test_cases = [
        # ① 氏名（PERSON）- spaCy NER
        {
            "text": "山田太郎さんは東京在住です。",
            "expected_entities": ["PERSON"],
            "description": "氏名検出（spaCy NER）"
        },

        # ② 電話番号（PHONE_NUMBER）
        {
            "text": "電話番号は03-1234-5678です。",
            "expected_entities": ["PHONE_NUMBER"],
            "description": "固定電話番号（ハイフンあり）"
        },
        {
            "text": "携帯は090-1234-5678です。",
            "expected_entities": ["PHONE_NUMBER"],
            "description": "携帯電話番号"
        },
        {
            "text": "連絡先：０９０－１２３４－５６７８",  # 全角
            "expected_entities": ["PHONE_NUMBER"],
            "description": "全角電話番号（NFKC正規化でテスト）"
        },

        # ③ メールアドレス（EMAIL_ADDRESS）
        {
            "text": "メールアドレスはtest@example.comです。",
            "expected_entities": ["EMAIL_ADDRESS"],
            "description": "メールアドレス"
        },

        # ④ 住所（JP_ADDRESS）
        {
            "text": "住所は東京都港区芝公園1-2-3です。",
            "expected_entities": ["JP_ADDRESS"],
            "description": "住所（都道府県＋市区町村＋番地）"
        },
        {
            "text": "〒100-0001 東京都千代田区千代田1-1",
            "expected_entities": ["JP_ADDRESS"],
            "description": "郵便番号付き住所"
        },

        # ⑤ 生年月日（DATE_TIME）
        {
            "text": "生年月日は1990年5月15日です。",
            "expected_entities": ["DATE_TIME"],
            "description": "西暦生年月日（年月日）"
        },
        {
            "text": "誕生日は平成2年5月15日です。",
            "expected_entities": ["DATE_TIME"],
            "description": "和暦生年月日"
        },
        {
            "text": "生まれは2000/05/15です。",
            "expected_entities": ["DATE_TIME"],
            "description": "スラッシュ区切り生年月日"
        },

        # ⑥ 銀行口座番号（JP_BANK_ACCOUNT）
        {
            "text": "口座番号は1234567です。",
            "expected_entities": ["JP_BANK_ACCOUNT"],
            "description": "銀行口座番号（7桁）"
        },
        {
            "text": "普通1234567の口座です。",
            "expected_entities": ["JP_BANK_ACCOUNT"],
            "description": "口座種別＋口座番号"
        },
        {
            "text": "銀行口座は1234-123-1234567です。",
            "expected_entities": ["JP_BANK_ACCOUNT"],
            "description": "銀行コード＋支店コード＋口座番号"
        },

        # ⑦ マイナンバー（JP_MY_NUMBER）
        {
            "text": "マイナンバーは123456789012です。",
            "expected_entities": ["JP_MY_NUMBER"],
            "description": "マイナンバー（12桁）"
        },
        {
            "text": "個人番号は1234-5678-9012です。",
            "expected_entities": ["JP_MY_NUMBER"],
            "description": "マイナンバー（ハイフン区切り）"
        },

        # ⑧ クレジットカード番号（CREDIT_CARD）
        {
            "text": "クレジットカード番号は4111-1111-1111-1111です。",
            "expected_entities": ["CREDIT_CARD"],
            "description": "クレジットカード番号（Visa、Luhnチェック通過）"
        },
        {
            "text": "カード番号：５５００－００００－００００－０００４",  # 全角
            "expected_entities": ["CREDIT_CARD"],
            "description": "全角クレジットカード番号（MasterCard）"
        },

        # 複合テスト
        {
            "text": """
            氏名：山田太郎
            電話：03-1234-5678
            メール：yamada@example.com
            住所：東京都港区芝公園1-2-3
            生年月日：1990年5月15日
            マイナンバー：1234-5678-9012
            """,
            "expected_entities": ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "JP_ADDRESS", "DATE_TIME", "JP_MY_NUMBER"],
            "description": "複合PII検出"
        },
    ]

    print("=" * 80)
    print("Presidio日本語PII検出テスト")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = set(test_case["expected_entities"])
        description = test_case["description"]

        # ② NFKC正規化（全角→半角）
        text_normalized = unicodedata.normalize("NFKC", text)

        # PII検出
        results = analyzer.analyze(text=text_normalized, language="ja")
        detected = set(r.entity_type for r in results)

        # 結果判定
        success = expected.issubset(detected)
        status = "✓ PASS" if success else "✗ FAIL"

        if success:
            passed += 1
        else:
            failed += 1

        print(f"Test {i}: {status} - {description}")
        print(f"  入力: {text.strip()[:60]}...")
        print(f"  期待: {sorted(expected)}")
        print(f"  検出: {sorted(detected)}")

        if results:
            print("  詳細:")
            for r in results:
                detected_text = text_normalized[r.start:r.end]
                print(f"    - {r.entity_type} (score={r.score:.2f}): '{detected_text}'")

        print()

    print("=" * 80)
    print(f"結果: {passed} passed, {failed} failed (合計 {passed + failed} テスト)")
    print("=" * 80)


def main():
    print("セットアップ中...")
    print("（初回実行時はspaCyモデルのダウンロードが必要な場合があります）")
    print()

    try:
        analyzer = setup_analyzer()
        print("セットアップ完了")
        print()
        test_pii_detection(analyzer)
    except Exception as e:
        print(f"エラー: {e}")
        print()
        print("spaCyモデルがインストールされていない場合は、以下を実行してください:")
        print("  python -m spacy download ja_core_news_trf")


if __name__ == "__main__":
    main()
