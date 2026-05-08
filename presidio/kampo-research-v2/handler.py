import os
import random
import unicodedata
import boto3
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from recognizers.japanese_standard import get_all_japanese_recognizers
from text_normalizer import normalize_japanese_text

# --- 初期化（Lambda コールドスタート時に1度だけ実行） ---

_nlp_config = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
}
nlp_engine = NlpEngineProvider(nlp_configuration=_nlp_config).create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

# 日本語標準PII Recognizerを登録（code-document.md準拠）
for recognizer in get_all_japanese_recognizers():
    analyzer.registry.add_recognizer(recognizer)

batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
anonymizer = AnonymizerEngine()

s3 = boto3.client("s3")
OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET", "default-bucket")

# PERSON エンティティをカタカナにランダム置換
_KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

def _katakana_replacer(entity: str) -> str:
    return "".join(random.choices(_KATAKANA, k=len(entity)))

# エンティティ種別ごとの匿名化オペレーター
_OPERATORS = {
    "DEFAULT":         OperatorConfig("replace", {}),
    "PERSON":          OperatorConfig("custom", {"lambda": _katakana_replacer}),
    "PHONE_NUMBER":    OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8,  "from_end": False}),
    "CREDIT_CARD":     OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 14, "from_end": True}),
    "CREDIT_CARD_CVV": OperatorConfig("replace", {"new_value": "***"}),
}


def mask_text(text: str) -> str:
    """
    テキストをマスキングする。
    前処理でかな数字・漢数字を半角数字に変換してから解析。
    """
    # 日本語テキスト正規化（NFKC + かな数字→漢数字→半角数字）
    text_normalized = normalize_japanese_text(text)

    results = analyzer.analyze(text=text_normalized, language="ja")
    if not results:
        return text_normalized
    return anonymizer.anonymize(text=text_normalized, analyzer_results=results, operators=_OPERATORS).text


# --- Lambda ハンドラ ---

def lambda_handler(event, context):
    # ローカルテスト用（S3 なしで直接テキストを渡せる）
    if "test_text" in event:
        raw = event["test_text"]
        # 日本語テキスト正規化
        text_normalized = normalize_japanese_text(raw)
        results = analyzer.analyze(text=text_normalized, language="ja")
        return {
            "masked": mask_text(raw),
            "detections": [
                {"entity": r.entity_type, "score": round(r.score, 3), "text": text_normalized[r.start:r.end]}
                for r in results
            ],
        }

    # 本番: S3 イベント — 複数レコードをバッチで一括解析
    records = event["Records"]

    keys_and_texts = []
    for record in records:
        src_bucket = record["s3"]["bucket"]["name"]
        src_key    = record["s3"]["object"]["key"]
        obj  = s3.get_object(Bucket=src_bucket, Key=src_key)
        text = obj["Body"].read().decode("utf-8")
        # 日本語テキスト正規化
        text_normalized = normalize_japanese_text(text)
        keys_and_texts.append((src_key, text_normalized))

    texts = [t for _, t in keys_and_texts]
    batch_results = batch_analyzer.analyze_iterator(texts=texts, language="ja")

    for (src_key, text), analysis in zip(keys_and_texts, batch_results):
        analysis = list(analysis)
        masked = (
            anonymizer.anonymize(text=text, analyzer_results=analysis, operators=_OPERATORS).text
            if analysis
            else text
        )
        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=f"masked/{src_key}",
            Body=masked.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )

    return {"statusCode": 200}
