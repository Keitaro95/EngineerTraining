from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
# 電話番号に特化したRecognizerクラス
from presidio_analyzer.predefined_recognizers import PhoneRecognizer
# クレジットカードに特化した Recognizerクラス
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer
# 独自のパターンをかく
from presidio_analyzer import Pattern

configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "ja", "model_name": "ja_core_news_trf"}
    ],
}

provider = NlpEngineProvider(nlp_configuration=configuration)

nlp_engine = provider.create_engine()

pattern = Pattern(
    name="credit_car_ja",
    score=0.3,
    regex=r"(?:[４4][0-9０-９]{3}|[５5][1-５0-５][0-9０-９]{2}|[３3][0-9０-９]{3}|[６6][0-9０-９]{3}|[１1][0-9０-９]{3})[ー－\- 　]?(?:[0-9０-９]{4}[ー－\- 　]?){2}[0-9０-９]{4}"
)
credit_card_recognizer = CreditCardRecognizer(
    supported_entity="CREDIT_CARD",
    patterns=[pattern],
    supported_language="ja",
    replacement_pairs=[("-", ""), (" ", ""), ("ー", ""), ("ー", "")]
)


phone_recognizer = PhoneRecognizer(
    supported_regions=["JP"],
    supported_language="ja",
    context=["電話"]
)

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])
# analyzerのレジストリにphone_recognizer を追加
analyzer.registry.add_recognizer(phone_recognizer)
# analyzerのレジストリにクレジットカード認識 を追加
analyzer.registry.add_recognizer(credit_card_recognizer)

# ここに電話番号
sample_text = "豆蔵太郎の電話番号は029-123-5678です。クレジットカード番号は４５００ー１２３４ー５６７８ー９０１２です。"

results = analyzer.analyze(
    text = sample_text,
    entities=["PERSON", "PHONE_NUMBER", "CREDIT_CARD"],
    language="ja"
)

# entity: 検出されたエンティティのタイプ (PERSON, PHONE_NUMBER)。
# start/end: テキスト内の検出位置。
# score: 検出の信頼度スコア(0〜1の範囲)
"""
entity: PERSON, start: 0, end: 4, score: 0.85
entity: PHONE_NUMBER, start: 10, end: 23, score: 0.4
"""

from presidio_anonymizer import AnonymizerEngine

# 匿名化エンジンをインスタンスに
anonymizer = AnonymizerEngine()
# anonymizer.anonymizeで対象textをマスキングする
anonymized_text = anonymizer.anonymize(
    text=sample_text,
    analyzer_results=results,  # type: ignore
    
    )

for item in anonymized_text.items:
    print(f"entity: {item.entity_type}, start: {item.start}, end: {item.end}, text: {item.text}, operator: {item.operator}")
print(f"匿名化結果: {anonymized_text}")