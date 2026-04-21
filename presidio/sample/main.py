from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "ja", "model_name": "ja_core_news_trf"}
    ],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

# ここに電話番号
sample_text = "豆蔵太郎の電話番号は080-1234-5678です。"

results = analyzer.analyze(
    text = sample_text,
    entities=["PERSON", "PHONE_NUMBER"],
    language="ja"
)

# entity: 検出されたエンティティのタイプ (PERSON, PHONE_NUMBER)。
# start/end: テキスト内の検出位置。
# score: 検出の信頼度スコア(0〜1の範囲)。
# for result in results:
#     print(f"entity: {result.entity_type}, start: {result.start}, end: {result.end}, score: {result.score}")
"""
entity: PERSON, start: 0, end: 4, score: 0.85
entity: PHONE_NUMBER, start: 10, end: 23, score: 0.4
"""

from presidio_anonymizer import AnonymizerEngine

# 匿名化エンジンをインスタンスに
anonymizer = AnonymizerEngine()
# anonymizer.anonymizeで対象textをマスキングする
anonymized_text = anonymizer.anonymize(text=sample_text, analyzer_results=results) # type: ignore

for item in anonymized_text.items:
    print(f"entity: {item.entity_type}, start: {item.start}, end: {item.end}, text: {item.text}, operator: {item.operator}")
print(f"匿名化結果: {anonymized_text}")