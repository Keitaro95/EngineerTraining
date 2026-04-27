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
    """マイナンバー: 12桁（連続・スペース区切り・ハイフン区切り）"""
    PATTERNS = [
        Pattern("my_number_plain",  r"(?<!\d)\d{12}(?!\d)", score=0.6),
        Pattern("my_number_spaced", r"(?<!\d)\d{4}[\s　]\d{4}[\s　]\d{4}(?!\d)", score=0.6),
        Pattern("my_number_hyphen", r"(?<!\d)\d{4}[-－]\d{4}[-－]\d{4}(?!\d)", score=0.6),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="JP_MY_NUMBER",
            patterns=self.PATTERNS,
            context=["マイナンバー", "個人番号"],
            supported_language="ja",
        )


class BankAccountRecognizer(PatternRecognizer):
    """銀行口座: 7桁、または支店コード3桁+口座番号7桁"""
    def __init__(self):
        super().__init__(
            supported_entity="JP_BANK_ACCOUNT",
            patterns=[
                Pattern("bank_account_7digit",        r"(?<!\d)\d{7}(?!\d)",                  score=0.3),
                Pattern("bank_account_branch_account", r"(?<!\d)\d{3}[-－\s　]\d{7}(?!\d)", score=0.5),
            ],
            context=["口座", "銀行", "普通", "当座", "口座番号"],
            supported_language="ja",
        )


class JapanesePhoneRecognizer(PatternRecognizer):
    """日本の電話番号（固定・携帯・IP・フリーダイヤル）"""
    PATTERNS = [
        # 市外局番2桁: 03-XXXX-XXXX, 06-XXXX-XXXX
        Pattern("landline_2digit",  r"0[36][-－]\d{4}[-－]\d{4}", score=0.75),
        # 携帯・IP電話: 090/080/070/050-XXXX-XXXX
        Pattern("mobile",           r"0[5789]0[-－]\d{4}[-－]\d{4}", score=0.75),
        # 市外局番3桁: 045-XXX-XXXX, 046-XXXX-XXXX など
        Pattern("landline_3digit",  r"0\d{2}[-－]\d{3,4}[-－]\d{4}", score=0.7),
        # 市外局番4桁: 0422-XX-XXXX, 0466-XX-XXXX など
        Pattern("landline_4digit",  r"0\d{3}[-－]\d{2}[-－]\d{4}", score=0.7),
        # フリーダイヤル: 0120-XXX-XXX
        Pattern("tollfree",         r"0120[-－]\d{3}[-－]\d{3}", score=0.8),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=self.PATTERNS,
            context=["電話", "携帯", "直通", "代表", "連絡先", "TEL", "tel"],
            supported_language="ja",
        )


class PolicyRecognizer(PatternRecognizer):
    """かんぽ証券番号: 10-14桁の英数字"""
    def __init__(self):
        super().__init__(
            supported_entity="JP_KAMPO_POLICY",
            patterns=[Pattern("kampo_policy", r"\b[A-Z0-9]{10,14}\b", score=0.4)],
            context=["証券番号", "保険"],
            supported_language="ja",
        )


class JapaneseDateRecognizer(PatternRecognizer):
    """日本の日付形式: 昭和50年3月15日、平成7年12月1日、令和3年4月22日など"""
    PATTERNS = [
        Pattern("era_date", r"(?:昭和|平成|令和|大正)\s*\d{1,2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日", score=0.7),
        Pattern("slash_date", r"\d{4}[/／]\d{1,2}[/／]\d{1,2}", score=0.6),
        Pattern("hyphen_date", r"\d{4}[-－]\d{1,2}[-－]\d{1,2}", score=0.6),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="JP_DATE",
            patterns=self.PATTERNS,
            context=["生年月日", "誕生日", "生まれ"],
            supported_language="ja",
        )


class JapaneseAddressRecognizer(PatternRecognizer):
    """日本の住所: 都道府県から始まる住所"""
    PATTERN = r"(?:東京都|北海道|(?:京都|大阪)府|(?:青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|神奈川|新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄)県)[぀-ゟ゠-ヿ一-鿿0-9０-９\-－ー]+(?:市|区|町|村)[぀-ゟ゠-ヿ一-鿿0-9０-９\-－ー]+"

    def __init__(self):
        super().__init__(
            supported_entity="JP_ADDRESS",
            patterns=[Pattern("jp_address", self.PATTERN, score=0.7)],
            context=["住所", "所在地", "居住"],
            supported_language="ja",
        )