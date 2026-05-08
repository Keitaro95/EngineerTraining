"""
Presidio日本語標準PII Recognizers

code-document.mdの実装方針に基づく日本語PII検出用Recognizerの実装。
以下の8つのPII項目に対応:
① 氏名（PERSON）- spaCy NER使用
② 電話番号（PHONE_NUMBER）- PhoneRecognizer
③ メールアドレス（EMAIL_ADDRESS）- EmailRecognizer
④ 住所（JP_ADDRESS）- 自作PatternRecognizer
⑤ 生年月日（DATE_TIME）- 自作PatternRecognizer
⑥ 銀行口座番号（JP_BANK_ACCOUNT）- 自作PatternRecognizer
⑦ マイナンバー（JP_MY_NUMBER）- 自作PatternRecognizer
⑧ クレジットカード番号（CREDIT_CARD）- カスタマイズ版CreditCardRecognizer
"""

from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.predefined_recognizers import (
    PhoneRecognizer,
    EmailRecognizer,
    CreditCardRecognizer,
)


# ② 電話番号（PHONE_NUMBER）
def create_japanese_phone_recognizer():
    """
    日本の電話番号を検出するPhoneRecognizer。
    supported_regions=["JP"]で日本の電話番号フォーマットに対応。
    市外局番03、携帯080/090、050のIP電話、0120フリーダイヤル等を検出。
    """
    return PhoneRecognizer(
        supported_regions=["JP"],
        supported_language="ja",
        context=["電話", "TEL", "携帯", "連絡先", "電話番号"]
    )


# ③ メールアドレス（EMAIL_ADDRESS）
def create_japanese_email_recognizer():
    """
    メールアドレスを検出するEmailRecognizer。
    正規表現は言語非依存なので、contextのみ日本語化。
    """
    return EmailRecognizer(
        supported_language="ja",
        context=["メール", "メールアドレス", "Eメール", "連絡先", "email"]
    )


# ④ 住所（JP_ADDRESS）
def create_japanese_address_recognizer():
    """
    日本の住所を検出するPatternRecognizer。
    都道府県＋市区町村＋町名＋番地＋建物の構造に対応。
    郵便番号（〒付き・ハイフンあり/なし）にも対応。
    """
    address_pattern = Pattern(
        name="jp_address",
        regex=r"(?:〒?\d{3}-?\d{4})?\s*(?:北海道|(?:京都|大阪)府|東京都|.{2,3}県)[^\s、。]+?[市区町村][^\s、。]+?(?:\d+(?:[-]\d+)*)?",
        score=0.5
    )
    return PatternRecognizer(
        supported_entity="JP_ADDRESS",
        patterns=[address_pattern],
        supported_language="ja",
        context=["住所", "在住", "所在地", "番地", "丁目"]
    )


# ⑤ 生年月日（DATE_TIME）
def create_japanese_date_recognizer():
    """
    日本の日付フォーマットを検出するPatternRecognizer。
    和暦（明治/大正/昭和/平成/令和）と西暦の両方に対応。
    クレジットカード有効期限（MM/YY形式）も統合。
    """
    dob_patterns = [
        # 和暦：令和5年3月15日、平成10年5月3日等
        Pattern(
            name="jp_date_kanji",
            regex=r"(?:明治|大正|昭和|平成|令和)?\d{1,4}年\s*\d{1,2}月\s*\d{1,2}日",
            score=0.6
        ),
        # 西暦スラッシュ：2000/1/1、2000-01-01、2000.1.1等
        Pattern(
            name="jp_date_slash",
            regex=r"(?:19|20)\d{2}[/／\-－．\.]\d{1,2}[/／\-－．\.]\d{1,2}",
            score=0.4
        ),
        # 和暦略記：H10.5.3、R5.3.15等
        Pattern(
            name="jp_date_abbrev",
            regex=r"[MTSHR明大昭平令][0-9０-９]{1,2}[\.\．][0-9０-９]{1,2}[\.\．][0-9０-９]{1,2}",
            score=0.5
        ),
        # クレカ有効期限：12/28、01/25等（MM/YY形式）
        Pattern(
            name="credit_card_expiry",
            regex=r"\b(?:0?[1-9]|1[0-2])[/／]\d{2}\b",
            score=0.4
        ),
    ]
    return PatternRecognizer(
        supported_entity="DATE_TIME",
        patterns=dob_patterns,
        supported_language="ja",
        context=["生年月日", "誕生日", "生まれ", "DOB", "生年", "年齢", "有効期限", "期限"]
    )


# ⑥ 銀行口座番号（JP_BANK_ACCOUNT）
def create_japanese_bank_account_recognizer():
    """
    日本の銀行口座番号を検出するPatternRecognizer。
    銀行コード(4桁)＋支店コード(3桁)＋口座番号(7桁)の形式に対応。
    口座種別＋口座番号のパターン（普通1234567）にも対応。
    """
    bank_patterns = [
        # 銀行コード＋支店コード＋口座番号：1234-123-1234567
        Pattern(
            name="jp_bank_full",
            regex=r"\b\d{4}[\s\-－ー]?\d{3}[\s\-－ー]?\d{7}\b",
            score=0.5
        ),
        # 口座種別＋口座番号：普通1234567、当座1234567
        Pattern(
            name="jp_bank_type_number",
            regex=r"(?:普通|当座)\s*\d{7}\b",
            score=0.6
        ),
        # 口座番号のみ（7桁、contextに依存）
        Pattern(
            name="jp_bank_number_only",
            regex=r"\b\d{7}\b",
            score=0.3
        ),
    ]
    return PatternRecognizer(
        supported_entity="JP_BANK_ACCOUNT",
        patterns=bank_patterns,
        supported_language="ja",
        context=["銀行", "口座", "支店", "普通", "当座", "預金", "口座番号"]
    )


# ⑦ マイナンバー（JP_MY_NUMBER）
def create_japanese_my_number_recognizer():
    """
    マイナンバー（個人番号）を検出するPatternRecognizer。

    パターンA：「マイナンバーは1234-5678-9012です。」（半角数字＋ハイフン区切り）
    パターンB：「個人番号は123456789012です。」（半角数字12桁連続）

    統合正規表現：\b\d{12}\b|\b\d{4}[\s\-－ー]\d{4}[\s\-－ー]\d{4}\b
    """
    my_number_patterns = [
        # パターンA・B統合：ハイフン区切りまたは連続12桁
        Pattern(
            name="my_number_standard",
            regex=r"\b\d{12}\b|\b\d{4}[\s\-－ー]\d{4}[\s\-－ー]\d{4}\b",
            score=0.4
        ),
    ]
    return PatternRecognizer(
        supported_entity="JP_MY_NUMBER",
        patterns=my_number_patterns,
        supported_language="ja",
        context=["マイナンバー", "個人番号", "マイナンバーカード", "個人識別番号"]
    )


# ⑧ クレジットカード番号（CREDIT_CARD）
def create_japanese_credit_card_recognizer():
    """
    クレジットカード番号を検出するCreditCardRecognizer。
    日本語対応版：IINプレフィックスで先頭を絞り込み、
    Luhnチェックサム検証で誤検出を削減。
    4=Visa、5=MasterCard、3=Amex/JCB等
    """
    credit_card_pattern = Pattern(
        name="credit_card_ja",
        score=0.3,
        # IINプレフィックスで絞り込み：Visa(4xxx)、MasterCard(51-55xx)、
        # Amex(34xx/37xx)、JCB(35xx)、Diners(36xx)
        regex=r"(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|35\d{2}|36\d{2})[\-\s－]?(?:\d{4}[\-\s－]?){2}\d{4}"
    )
    return CreditCardRecognizer(
        patterns=[credit_card_pattern],
        supported_language="ja",
        context=[
            "クレジット", "カード", "カード番号",
            "VISA", "Master", "MasterCard", "JCB",
            "Amex", "American Express", "クレカ"
        ],
        # Luhnチェック前に削除する記号
        replacement_pairs=[("-", ""), ("－", ""), (" ", ""), ("　", "")]
    )


# 全Recognizerを取得する便利関数
def get_all_japanese_recognizers():
    """
    日本語標準PII検出用の全Recognizerを返す。
    ① 氏名（PERSON）はspaCy NERで検出されるためRecognizerは不要。
    """
    return [
        create_japanese_phone_recognizer(),           # ②
        create_japanese_email_recognizer(),           # ③
        create_japanese_address_recognizer(),         # ④
        create_japanese_date_recognizer(),            # ⑤
        create_japanese_bank_account_recognizer(),    # ⑥
        create_japanese_my_number_recognizer(),       # ⑦
        create_japanese_credit_card_recognizer(),     # ⑧
    ]