# Presidio日本語対応 実装方針

## 全体方針

Presidio公式は日本語のデフォルト設定を提供していないため、NLPエンジンを日本語モデルに切り替えた上で、各Recognizerを日本語向けにカスタマイズして登録する。各Recognizerは`supported_language`を1つしか持たないため、日本語版を個別にインスタンス化してregistryに追加する形を取る。

### 前提セットアップ

**① NLPエンジンに日本語モデルを設定**

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])
```

事前に `python -m spacy download ja_core_news_trf` でモデルをダウンロードしておく。

**② 入力テキストの前処理（必須）**

analyze実行前に必ずNFKC正規化で全角数字・全角記号を半角に変換する。これがあるかないかで電話番号・銀行口座・マイナンバー・クレジットカードの検出精度が大きく変わる。

```python
import unicodedata

text_normalized = unicodedata.normalize("NFKC", text)  # 全角→半角
results = analyzer.analyze(text=text_normalized, language="ja", entities=[...])
```

NFKC正規化を入れておけば、各Recognizerの正規表現に全角対応を埋め込む必要がなくなり、コードがシンプルになる。

---

## 各PII項目の対応方針

### ① 氏名（PERSON）— 組み込みのspaCy NERをそのまま使う

`ja_core_news_trf`が固有表現認識（NER）として人名を抽出する。Recognizerの追加実装は不要で、`analyze`時に`entities=["PERSON"]`を指定するだけで動く。

```python
results = analyzer.analyze(
    text=text_normalized,
    entities=["PERSON"],
    language="ja"
)
```

精度はspaCyモデル依存。検出漏れが多い場合は`ja_ginza`等の別モデルへの切替や、特定の名前についてはdeny_list方式の追加Recognizerで補強する。

---

### ② 電話番号（PHONE_NUMBER）— PhoneRecognizerに`supported_regions=["JP"]`を指定

PhoneRecognizerは内部でGoogleの`phonenumbers`ライブラリを使用しており、`supported_regions=["JP"]`を渡すと日本のフォーマット（市外局番03、携帯080/090、050のIP電話、0120フリーダイヤル等）を網羅的に検出できる。Googleが各国の電話番号形式をメンテしている標準ライブラリなので、regionの指定だけで基本は信頼できる。

参考：[phone_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/phone_recognizer.py)

デフォルトの`DEFAULT_SUPPORTED_REGIONS`は`("US", "UK", "DE", "FE", "IL", "IN", "CA", "BR")`で日本は含まれていないので、明示的に`JP`を指定する必要がある。

```python
from presidio_analyzer.predefined_recognizers import PhoneRecognizer

phone_recognizer = PhoneRecognizer(
    supported_regions=["JP"],
    supported_language="ja",
    context=["電話", "TEL", "携帯", "連絡先"]
)
analyzer.registry.add_recognizer(phone_recognizer)
```

`context`に日本語の文脈ワードを入れると、Context Enhancementによりスコアが0.4→0.75に上がる。全角数字の電話番号は事前のNFKC正規化で対応済み。

---

### ③ メールアドレス（EMAIL_ADDRESS）— EmailRecognizerをそのまま使い、contextだけ日本語化

メールアドレスの正規表現は言語に依存しないので、組み込みクラスをそのまま使える。`supported_language="ja"`を指定し、contextを日本語に置き換えるだけ。

参考：[email_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/email_recognizer.py)

```python
from presidio_analyzer.predefined_recognizers import EmailRecognizer

email_recognizer = EmailRecognizer(
    supported_language="ja",
    context=["メール", "メールアドレス", "Eメール", "連絡先"]
)
analyzer.registry.add_recognizer(email_recognizer)
```

---

### ④ 住所（JP_ADDRESS）— 公式Recognizerが存在しないので自作

Presidioに住所専用のRecognizerは存在しない。spaCyのNERで「東京都」「港区」などはLOCATIONとして部分的に検出されるが、番地や建物名は拾えないため、住所全体としては不完全。日本の住所構造（都道府県＋市区町村＋町名＋番地＋建物）に沿ったPatternRecognizerを自作する。

```python
from presidio_analyzer import Pattern, PatternRecognizer

address_pattern = Pattern(
    name="jp_address",
    regex=r"(?:〒?\d{3}-?\d{4})?\s*(?:北海道|(?:京都|大阪)府|東京都|.{2,3}県)[^\s、。]+?[市区町村][^\s、。]+?(?:\d+(?:[-]\d+)*)?",
    score=0.5
)
address_recognizer = PatternRecognizer(
    supported_entity="JP_ADDRESS",
    patterns=[address_pattern],
    supported_language="ja",
    context=["住所", "在住", "所在地"]
)
analyzer.registry.add_recognizer(address_recognizer)
```

spaCyのLOCATION検出と併用する形で「都道府県名は組み込みNER」「番地まで含む完全な住所はカスタムRegex」と役割分担する形になる。

---

### ⑤ 生年月日（DATE_TIME）— DateRecognizerは英米式しか対応していないため自作

組み込みのDateRecognizerはMM/DD/YYYY、DD-MM-YYYY等の英米式の日付フォーマットしか対応しておらず、「2000年1月1日」「平成10年5月3日」「H10.5.3」等の日本式表記は検出できない。

参考：[date_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/date_recognizer.py)

PatternRecognizerで自作する。和暦・西暦の両方に対応できるよう複数パターンを登録する。

```python
dob_patterns = [
    Pattern(
        name="jp_date_kanji",
        regex=r"(?:明治|大正|昭和|平成|令和)?\d{1,4}年\s*\d{1,2}月\s*\d{1,2}日",
        score=0.6
    ),
    Pattern(
        name="jp_date_slash",
        regex=r"(?:19|20)\d{2}[/／\-．\.]\d{1,2}[/／\-．\.]\d{1,2}",
        score=0.4
    ),
]
dob_recognizer = PatternRecognizer(
    supported_entity="DATE_TIME",
    patterns=dob_patterns,
    supported_language="ja",
    context=["生年月日", "誕生日", "生まれ", "DOB"]
)
analyzer.registry.add_recognizer(dob_recognizer)
```

---

### ⑥ 銀行口座番号（JP_BANK_ACCOUNT, SPII）— PatternRecognizerで自作

日本の銀行口座は「銀行コード(4桁)＋支店コード(3桁)＋口座種別(1桁)＋口座番号(7桁)」が基本。IbanRecognizerは欧州規格でJPには使えないため、自作PatternRecognizerが必要。

参考：[pattern_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/pattern_recognizer.py)

```python
bank_pattern = Pattern(
    name="jp_bank_account",
    regex=r"\b\d{4}[\s\-]?\d{3}[\s\-]?\d{7}\b|\b(?:普通|当座)\s*\d{7}\b",
    score=0.5
)
bank_recognizer = PatternRecognizer(
    supported_entity="JP_BANK_ACCOUNT",
    patterns=[bank_pattern],
    supported_language="ja",
    context=["銀行", "口座", "支店", "普通", "当座"]
)
analyzer.registry.add_recognizer(bank_recognizer)
```

---

### ⑦ マイナンバー（JP_MY_NUMBER, SPII）— PatternRecognizerで自作

マイナンバーは住民票を持つ全住民に付番される12桁の番号。12桁目はチェックディジット（11除算による検査用数字）。

参考：[pattern_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/pattern_recognizer.py)

**実装方針：まずはシンプル版で十分。** 数字パターン＋context（"マイナンバー"、"個人番号"）でスコアを上げる方式で実用上問題ない。マスキング目的なら誤検出されてもマスクされるだけなので過剰検出側で安全。

```python
my_number_pattern = Pattern(
    name="my_number_pattern",
    regex=r"\b\d{12}\b|\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b",
    score=0.3
)
my_number_recognizer = PatternRecognizer(
    supported_entity="JP_MY_NUMBER",
    patterns=[my_number_pattern],
    supported_language="ja",
    context=["マイナンバー", "個人番号", "マイナンバーカード"]
)
analyzer.registry.add_recognizer(my_number_recognizer)
```

将来、誤検出を減らしたくなった場合は、PatternRecognizerを継承してチェックディジット検証を`validate_result`に実装する。マイナンバーの数字ルール（1〜11桁目に重み[6,5,4,3,2,7,6,5,4,3,2]を掛けて11で除算、その余りからチェックディジットを算出）に従う。

---

### ⑧ クレジットカード番号（CREDIT_CARD, SPII）— CreditCardRecognizerをカスタマイズ

CreditCardRecognizerは英語・スペイン語等のみのサポートで、日本語には対応していない。原因は、`\b`（単語境界）と全角文字非対応。ただし**Luhnチェックサム検証は内蔵されているので、日本語対応版にカスタマイズすればこの検証は引き続き効く**。これにより、ハイフン付きの単なる16桁数字が誤検出される可能性は大幅に減る（Luhnチェック失敗時はscore=0.0）。

参考：[credit_card_recognizer.py](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/credit_card_recognizer.py)

```python
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer

credit_card_pattern = Pattern(
    name="credit_card_ja",
    score=0.3,
    regex=r"(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|3[5]\d{2}|6\d{3})[\-\s]?(?:\d{4}[\-\s]?){2}\d{4}"
)
credit_card_recognizer = CreditCardRecognizer(
    patterns=[credit_card_pattern],
    supported_language="ja",
    context=["クレジット", "カード", "カード番号", "VISA", "Master", "JCB", "Amex"],
    replacement_pairs=[("-", ""), (" ", "")]
)
analyzer.registry.add_recognizer(credit_card_recognizer)
```

ポイント：
- IINプレフィックス（4=Visa、5=Master、3=Amex/JCB等）で先頭1桁を絞り込む
- `replacement_pairs`はLuhnチェック前に削除する記号で、ハイフン・スペースを除去してからチェックサム検証を通す
- Luhnチェックを通過するとscoreが1.0、失敗時は0.0になる
- 全角文字は事前のNFKC正規化で半角化済みなので、regex内で全角対応する必要なし
- 偽陽性をさらに減らしたい場合は`score_threshold=0.6`のような閾値運用で「Luhn通過＋context一致」のみを採用する

---

## まとめ表

| # | 項目 | 区分 | 対応方針 | カスタム要否 |
|---|---|---|---|---|
| ① | 氏名 | PII | spaCy NER任せ。`entities=["PERSON"]`指定のみ | 不要 |
| ② | 電話番号 | PII | `PhoneRecognizer(supported_regions=["JP"])` | 設定変更のみ |
| ③ | メールアドレス | PII | `EmailRecognizer`をそのまま使い、contextを日本語化 | 設定変更のみ |
| ④ | 住所 | PII | PatternRecognizerで自作＋spaCy LOCATIONと併用 | **自作必須** |
| ⑤ | 生年月日 | PII | 和暦・西暦両対応のPatternRecognizerを自作 | **自作必須** |
| ⑥ | 銀行口座番号 | SPII | PatternRecognizerで自作 | **自作必須** |
| ⑦ | マイナンバー | SPII | PatternRecognizerで自作（最初はregex+contextで十分。必要に応じてチェックディジット検証追加） | **自作必須** |
| ⑧ | クレジットカード番号 | SPII | CreditCardRecognizerをカスタマイズ（Luhnチェックは継承される） | **カスタマイズ必須** |

## 実装の流れ

1. `python -m spacy download ja_core_news_trf` で日本語モデル取得
2. `NlpEngineProvider`で日本語NLPエンジンを構築
3. `AnalyzerEngine`に日本語エンジンを渡す
4. 各Recognizer（②③⑥⑦⑧と④⑤の自作分）を順に`analyzer.registry.add_recognizer()`で登録
5. analyze実行前に`unicodedata.normalize("NFKC", text)`で前処理
6. `analyzer.analyze(text=text_normalized, language="ja", entities=[...])`で検出