# Presidio 日本語対応実装

`code-document.md`の実装方針に基づいた、Presidioの日本語PII検出システムです。

## 概要

Microsoft Presidioを使用して、日本語テキストから個人情報（PII）と特定個人情報（SPII）を検出・マスキングします。

## 対応PII項目

### 日本語標準PII（`recognizers/japanese_standard.py`）

| # | 項目 | Entity Type | 区分 | 実装方法 |
|---|---|---|---|---|
| ① | 氏名 | `PERSON` | PII | spaCy NER（`ja_core_news_trf`） |
| ② | 電話番号 | `PHONE_NUMBER` | PII | `PhoneRecognizer(supported_regions=["JP"])` |
| ③ | メールアドレス | `EMAIL_ADDRESS` | PII | `EmailRecognizer` |
| ④ | 住所 | `JP_ADDRESS` | PII | PatternRecognizer（自作） |
| ⑤ | 生年月日 | `DATE_TIME` | PII | PatternRecognizer（自作、和暦・西暦対応） |
| ⑥ | 銀行口座番号 | `JP_BANK_ACCOUNT` | SPII | PatternRecognizer（自作） |
| ⑦ | マイナンバー | `JP_MY_NUMBER` | SPII | PatternRecognizer（自作） |
| ⑧ | クレジットカード番号 | `CREDIT_CARD` | SPII | `CreditCardRecognizer`（カスタマイズ、Luhnチェック有効） |

### カスタムPII（`recognizers/japanese_custom.py`）

業務固有のPII項目：

- `MZ_EMP_NUMBER`: 社員番号（MZ-YYYY-NNNNNN形式）
- `JP_MY_NUMBER`: マイナンバー（チェックディジット検証版）
- `JP_BANK_ACCOUNT`: 銀行口座番号（簡易版）
- `JP_KAMPO_POLICY`: かんぽ証券番号

## 主要機能

### 1. NFKC正規化（必須前処理）

全角数字・全角記号を半角に変換することで、電話番号・銀行口座・マイナンバー・クレジットカードの検出精度が向上します。

```python
import unicodedata
text_normalized = unicodedata.normalize("NFKC", text)
```

### 2. Context Enhancement

日本語の文脈ワード（"電話"、"メール"、"住所" など）により、スコアが自動的に向上します。

### 3. Luhnチェックサム検証（クレジットカード）

`CreditCardRecognizer`は内蔵のLuhnアルゴリズムで、単なる16桁数字の誤検出を削減します。

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. spaCy日本語モデルのダウンロード

```bash
python -m spacy download ja_core_news_trf
```

## 使い方

### テストの実行

```bash
python test_recognizers.py
```

8つの標準PII項目と業務固有PIIの検出をテストします。

### Lambda関数として使用

```python
from handler import lambda_handler

# ローカルテスト
event = {
    "test_text": "氏名：山田太郎 電話：03-1234-5678 メール：test@example.com"
}
result = lambda_handler(event, None)
print(result["masked"])
print(result["detections"])
```

### スタンドアロンで使用

```python
import unicodedata
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from recognizers.japanese_standard import get_all_japanese_recognizers

# NLPエンジンの設定
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ja", "model_name": "ja_core_news_trf"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

# Analyzerの初期化
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

# Recognizerの登録
for recognizer in get_all_japanese_recognizers():
    analyzer.registry.add_recognizer(recognizer)

# PII検出（NFKC正規化は必須）
text = "電話番号は０３－１２３４－５６７８です。"  # 全角
text_normalized = unicodedata.normalize("NFKC", text)
results = analyzer.analyze(text=text_normalized, language="ja")

for result in results:
    print(f"{result.entity_type}: {text_normalized[result.start:result.end]} (score={result.score})")
```

## ファイル構成

```
for-kampo-research/
├── README.md                           # このファイル
├── code-document.md                    # 実装方針ドキュメント
├── handler.py                          # Lambda関数ハンドラ
├── test_recognizers.py                 # テストスクリプト
├── requirements.txt                    # Python依存パッケージ
├── Dockerfile                          # Dockerイメージビルド用
└── recognizers/
    ├── __init__.py
    ├── japanese_standard.py            # 日本語標準PII Recognizers
    └── japanese_custom.py              # カスタムPII Recognizers（業務固有）
```

## 実装のポイント

### NFKC正規化の重要性

全角数字・全角記号の入力に対応するため、**必ず**analyze実行前にNFKC正規化を適用してください。

❌ 悪い例：
```python
results = analyzer.analyze(text="電話：０３－１２３４－５６７８", language="ja")  # 検出できない
```

✓ 良い例：
```python
text_normalized = unicodedata.normalize("NFKC", "電話：０３－１２３４－５６７８")
results = analyzer.analyze(text=text_normalized, language="ja")  # 正しく検出
```

### スコア閾値の調整

デフォルトでは`score >= 0.0`で全て検出されます。誤検出を減らしたい場合は閾値を上げてください。

```python
results = analyzer.analyze(
    text=text_normalized,
    language="ja",
    score_threshold=0.5  # スコア0.5以上のみ
)
```

### Context Enhancementの効果

文脈ワードがあるとスコアが向上します。

- 「電話」がない場合: `PHONE_NUMBER` score=0.4
- 「電話」がある場合: `PHONE_NUMBER` score=0.75

### Luhnチェックの効果（クレジットカード）

- Luhnチェック通過: score=1.0
- Luhnチェック失敗: score=0.0

これにより、ハイフン付き16桁の単なる数字列の誤検出が大幅に減ります。

## デプロイ

### Dockerイメージのビルド

```bash
docker build -t presidio-japanese .
```

### AWS Lambda

1. ECRにプッシュ
2. Lambda関数を作成（コンテナイメージ）
3. 環境変数 `OUTPUT_BUCKET` を設定
4. S3トリガーを設定

## トラブルシューティング

### spaCyモデルが見つからない

```bash
python -m spacy download ja_core_news_trf
```

### 全角数字が検出されない

NFKC正規化を忘れていませんか？

```python
text_normalized = unicodedata.normalize("NFKC", text)
```

### 誤検出が多い

`score_threshold`を上げるか、contextを追加してください。

## 参考リンク

- [Presidio公式ドキュメント](https://microsoft.github.io/presidio/)
- [spaCy日本語モデル](https://spacy.io/models/ja)
- [code-document.md](./code-document.md) - 詳細な実装方針

## ライセンス

Presidio: MIT License
