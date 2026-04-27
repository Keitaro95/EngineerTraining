import re
from typing import Optional
from datetime import datetime
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, BatchAnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# class MyEmpNumberRecognizer(PatternRecognizer):
#     REGEX = r"[MＭ][ZＺ][\-－ー](?<year>[１1][９9][0-9０-９]{2}|[２2][０0][0-9０-９]{2})[\-－ー](?<seq>[0-9０-９]{6})"
#     PATTERNS = [
#         Pattern(
#             name=
#         )
#     ]



configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "ja", "model_name": "ja_core_news_trf"}
    ],
}
provider = NlpEngineProvider(nlp_configuration=configuration)

nlp_engine = provider.create_engine()

"""
自作Recognizerの作成 #
次に、Recognizerを自作してみます。
例として、組織固有の社員番号を識別するRecognizerを作成します。社員番号のフォーマットは以下と仮定します。

MZ-(固定値) + 数字4桁(入社年-西暦) + -(固定値) + 数字6桁(連番)
例）MZ-2000-000001
入社年は19xxまたは20xxのみ有効
全角文字を許容
このRecognizerを自作してみます。ここでは正規表現で社員番号を識別するPatternRecognizerを作成します。
"""

# パターンobjectを作る
# ただしこれは正規表現だけがルール
pattern = Pattern(
    name="mz_emp_number",
    regex=r"[MＭ][ZＺ][\-－ー](?:[１1][９9][0-9０-９]{2}|[２2][０0][0-9０-９]{2})[\-－ー][0-9０-９]{6}",
    score=0.5
)
emp_number_recognizer = PatternRecognizer(
    supported_entity="MZ_EMP_NUMBER",
    name="mz_emp_number",
    supported_language="ja",
    patterns=[pattern],
    context=["社員"]
)
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])
# ここで カスタムの recognizerを追加
analyzer.registry.add_recognizer(emp_number_recognizer)

# 自作のRecognizerクラスを作ってバリデーションロジックを追加する
class MyEmpNumberRecognizer(PatternRecognizer):
    REGEX = r"[MＭ][ZＺ][\-－ー](?P<year>[１1][９9][0-9０-９]{2}|[２2][０0][0-9０-９]{2})[\-－ー](?P<seq>[0-9０-９]{6})"
    PATTERNS = [
        Pattern(
            name="mz_emp_number",
            regex=REGEX,
            score=0.3 # 正規表現一致だけだと低スコア
        )
    ]
    CONTEXT = ["社員"]

    def __init__(self):
        super().__init__(
            supported_entity='MZ_EMP_NUMBER',
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="ja",
        )
    
    def validate_result(self, pattern_text: str) -> Optional[bool]:
        # match = self.PATTERNS[0].compiled_regex.search(pattern_text)

        match = re.search(self.REGEX, pattern_text)

        if match is None:
            return False
        
        seq = int(match.group("seq"))

        if seq == 0 or seq == 999999:
            return False


        year = int(match.group("year"))
        current_year = datetime.now().year

        if year > current_year:
            return False
        elif current_year - 50 <= year <= current_year:
            return True
        else:
            return None

emp_number_recognizer = MyEmpNumberRecognizer()
analyzer.registry.add_recognizer(emp_number_recognizer)


sample_texts = [
    "MZ-2001-000001",
    "ＭＺー２００１ー０００００１", # 全角
    "社員番号: MZ-1990-000001", # 文脈補強
    "MZ-3001-000001", # 不正(入社年が3001年)
    "MZ-2001-000000", # 連番がオールゼロ
    "MZ-2001-999999", # 連番がオール9
    "MZ-2099-000001", # 不正な西暦(未来)
    "MZ-1900-000001"  # 不正な西暦(遠い過去)
]

"""
for sample_text in sample_texts:
    results = analyzer.analyze(
        text=sample_text,
        entities=["MZ_EMP_NUMBER"],
        language="ja"
    )
    print(f"text: {sample_text}, score:{results[0].score if len(results) > 0 else 'None'}")
"""

# バッチ処理。
# 1回1回analyzerを呼ばない。まとめて1回渡す。
batchAnalyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
batch_results = batchAnalyzer.analyze_iterator(
    texts=sample_texts,
    language="ja",
    entities=["MZ_EMP_NUMBER"]
)
for index, results in enumerate(batch_results):
    print(f"text: {sample_texts[index]}, score:{results[0].score if len(results) > 0 else 'None'}")


# 匿名化する時はこれ使う
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 匿名化エンジンをインスタンスに
anonymizer = AnonymizerEngine()
# anonymizer.anonymizeで対象textをマスキングする
anonymized_text = anonymizer.anonymize(
    text=sample_text,
    analyzer_results=results, # type: ignore
    operators={
        # エンティティ名（デフォルトはDEFAULT,）, operator名:replace, paramsで変化を定義
        # new_value：置換後の文字列
        "DEFAULT": OperatorConfig(operator_name="replace", params={"new_value": "*"}),
        "PHONE_NUMBER": OperatorConfig(operator_name="mask", params={"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
        "CREDIT_CARD": OperatorConfig(operator_name="mask", params={"masking_char": "*", "chars_to_mask": 14, "from_end": True})
    })

def replacer(entity: str):
    katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    return ''.join(random.choices(katakana, k=len(entity)))



for item in anonymized_text.items:
    print(f"entity: {item.entity_type}, start: {item.start}, end: {item.end}, text: {item.text}, operator: {item.operator}")
print(f"匿名化結果: {anonymized_text}")



anonymized_text = anonymizer.anonymize(
    text=sample_text,
    analyzer_results=results, # type: ignore
    operators={
        "PERSON": OperatorConfig(operator_name="custom", params={"lambda": replacer}),
    })

print(anonymized_text.text)


