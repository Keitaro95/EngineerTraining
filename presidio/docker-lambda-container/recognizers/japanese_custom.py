import re
from typing import Optional
from datetime import datetime
from presidio_analyzer import Pattern, PatternRecognizer


class MyEmpNumberRecognizer(PatternRecognizer):
    """社員番号: MZ-YYYY-NNNNNN (入社年は19xx or 20xx、連番は000001〜999998)"""
    REGEX = r"[MＭ][ZＺ][\-－ー](?P<year>[１1][９9][0-9０-９]{2}|[２2][０0][0-9０-９]{2})[\-－ー](?P<seq>[0-9０-９]{6})"
    PATTERNS = [
        Pattern(
            name="mz_emp_number",
            regex=REGEX,
            score=0.3,
        )
    ]
    CONTEXT = ["社員"]

    def __init__(self):
        super().__init__(
            supported_entity="MZ_EMP_NUMBER",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="ja",
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
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


class MyNumberRecognizer(PatternRecognizer):
    """マイナンバー: 12桁"""
    def __init__(self):
        super().__init__(
            supported_entity="JP_MY_NUMBER",
            patterns=[Pattern("my_number", r"\b\d{12}\b", score=0.6)],
            context=["マイナンバー", "個人番号"],
            supported_language="ja",
        )


class BankAccountRecognizer(PatternRecognizer):
    """銀行口座: 7桁（誤検知多いのでscoreを低めにしてcontextに依存）"""
    def __init__(self):
        super().__init__(
            supported_entity="JP_BANK_ACCOUNT",
            patterns=[Pattern("bank_account", r"\b\d{7}\b", score=0.3)],
            context=["口座", "銀行", "普通", "当座"],
            supported_language="ja",
        )


class PolicyRecognizer(PatternRecognizer):
    def __init__(self):
        super().__init__(
            supported_entity="JP_KAMPO_POLICY",
            patterns=[Pattern("kampo_policy", r"\b[A-Z0-9]{10,14}\b", score=0.4)],
            context=["証券番号", "保険"],
            supported_language="ja",
        )