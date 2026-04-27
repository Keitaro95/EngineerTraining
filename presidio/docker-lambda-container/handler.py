import os
import random
import boto3
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from recognizers.japanese_custom import (
    MyEmpNumberRecognizer,
    MyNumberRecognizer,
    BankAccountRecognizer,
    PolicyRecognizer,
)

# --- 初期化（Lambda コールドスタート時に1度だけ実行） ---

_nlp_config = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
}
nlp_engine = NlpEngineProvider(nlp_configuration=_nlp_config).create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])
for recognizer in (
    MyEmpNumberRecognizer(),
    MyNumberRecognizer(),
    BankAccountRecognizer(),
    PolicyRecognizer(),
):
    analyzer.registry.add_recognizer(recognizer)

batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
anonymizer = AnonymizerEngine()

s3 = boto3.client("s3")
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

# PERSON エンティティをカタカナにランダム置換
_KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

def _katakana_replacer(entity: str) -> str:
    return "".join(random.choices(_KATAKANA, k=len(entity)))

# エンティティ種別ごとの匿名化オペレーター
_OPERATORS = {
    "DEFAULT":      OperatorConfig("replace", {}),
    "PERSON":       OperatorConfig("custom", {"lambda": _katakana_replacer}),
    "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8,  "from_end": False}),
    "CREDIT_CARD":  OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 14, "from_end": True}),
}


def mask_text(text: str) -> str:
    results = analyzer.analyze(text=text, language="ja")
    if not results:
        return text
    return anonymizer.anonymize(text=text, analyzer_results=results, operators=_OPERATORS).text


# --- Lambda ハンドラ ---

def lambda_handler(event, context):
    # ローカルテスト用（S3 なしで直接テキストを渡せる）
    if "test_text" in event:
        raw = event["test_text"]
        results = analyzer.analyze(text=raw, language="ja")
        return {
            "masked": mask_text(raw),
            "detections": [
                {"entity": r.entity_type, "score": round(r.score, 3), "text": raw[r.start:r.end]}
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
        keys_and_texts.append((src_key, text))

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
