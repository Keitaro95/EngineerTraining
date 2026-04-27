import json
import sys
from pathlib import Path

# recognizers パッケージを解決するためにパスを追加
sys.path.insert(0, str(Path(__file__).parent / "local-detection-research"))

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from recognizers.japanese_custom import (
    MyEmpNumberRecognizer,
    MyNumberRecognizer,
    BankAccountRecognizer,
    PolicyRecognizer,
    JapaneseDateRecognizer,
    JapaneseAddressRecognizer,
    JapanesePhoneRecognizer,
)

INPUT_PATH = Path(__file__).parent / "local-detection-research/dummy_data.json"
OUTPUT_PATH = Path(__file__).parent / "local-detection-research/output.json"

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
    JapaneseDateRecognizer(),
    JapaneseAddressRecognizer(),
    JapanesePhoneRecognizer(),
    EmailRecognizer(supported_language="ja"),
):
    analyzer.registry.add_recognizer(recognizer)

anonymizer = AnonymizerEngine()

_ENTITY_LABELS = {
    "PERSON": "NAME",
    "PHONE_NUMBER": "PHONE",
    "EMAIL_ADDRESS": "EMAIL",
    "LOCATION": "LOCATION",
    "JP_ADDRESS": "ADDRESS",
    "DATE_TIME": "DATE",
    "JP_DATE": "DATE",
    "CREDIT_CARD": "CREDIT_CARD",
    "MZ_EMP_NUMBER": "EMP_NUMBER",
    "JP_MY_NUMBER": "MY_NUMBER",
    "JP_BANK_ACCOUNT": "BANK_ACCOUNT",
    "JP_KAMPO_POLICY": "POLICY_NUMBER",
    "ORGANIZATION": "ORGANIZATION",
    "URL": "URL",
}


def _create_label_replacer(entity_type: str):
    label = _ENTITY_LABELS.get(entity_type, "MASKED")
    def replacer(_: str) -> str:
        return f"<{label}>"
    return replacer


_OPERATORS = {
    entity_type: OperatorConfig("custom", {"lambda": _create_label_replacer(entity_type)})
    for entity_type in _ENTITY_LABELS
}
_OPERATORS["DEFAULT"] = OperatorConfig("custom", {"lambda": lambda _: "<MASKED>"})


def mask_text(text: str) -> tuple[str, list[dict]]:
    results = analyzer.analyze(text=text, language="ja")
    if not results:
        return text, []
    masked = anonymizer.anonymize(text=text, analyzer_results=results, operators=_OPERATORS).text
    detections = [
        {"entity": r.entity_type, "score": round(r.score, 3), "text": text[r.start:r.end]}
        for r in results
    ]
    return masked, detections


def mask_json(obj: object, all_detections: list[dict], path: str = "") -> object:
    if isinstance(obj, str):
        masked, detections = mask_text(obj)
        for d in detections:
            d["path"] = path
        all_detections.extend(detections)
        return masked
    if isinstance(obj, dict):
        return {k: mask_json(v, all_detections, f"{path}.{k}" if path else k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask_json(item, all_detections, f"{path}[{i}]") for i, item in enumerate(obj)]
    return obj


def main():
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    all_detections: list[dict] = []
    masked_data = mask_json(data, all_detections)

    result = {
        "masked": masked_data,
        "detections": all_detections,
    }

    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"written → {OUTPUT_PATH}")
    print(f"detections: {len(all_detections)} 件")


if __name__ == "__main__":
    main()
