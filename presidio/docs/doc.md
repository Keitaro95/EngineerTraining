
https://developer.mamezou-tech.com/blogs/2025/01/04/presidio-intro/


uv python pin 3.12
uv sync
uv add "numpy<2"  
`uv add presidio-analyzer presidio-anonymizer`
`uv run python -m spacy download ja_core_news_trf`

.venv/lib/python3.13/site-packages/ja_core_news_trf
にモデルは保存されます

`spacy.load('ja_core_news_trf')`



# ダウンロード
uv run python -m spacy download ja_core_news_trf

# ダウンロード後に場所を確認
uv run python -c "import ja_core_news_trf; print(ja_core_news_trf.__file__)"

---

# バージョン固定

Intel Mac (x86_64) + spaCy日本語モデル (`ja_core_news_trf`) を動かすために以下を固定。

## pyproject.toml

```toml
requires-python = ">=3.12,<3.13"

dependencies = [
    "numpy>=1.0,<2.0",      # NumPy 2.x はspaCy/torchのwheelと非互換
    "spacy==3.8.14",         # torch 2.2.2 と依存解決できるバージョン
    "torch==2.2.2",          # Intel Mac + Python 3.12 で動作確認済み
    "presidio-analyzer>=2.2.362",
    "presidio-anonymizer>=2.2.362",
    ...
]
```

## バージョン固定の理由

| 設定 | 固定値 | 理由 |
|------|--------|------|
| Python | `>=3.12,<3.13` | 3.13以上はspaCy/torchのwheelなし、3.14もNG |
| numpy | `<2.0` | NumPy 2.x はspaCy・torchのコンパイル済みwheelと非互換 |
| torch | `==2.2.2` | Intel Mac (x86_64) + Python 3.12 で動く最新版。2.5.0以降はIntel Mac wheel廃止 |
| spacy | `==3.8.14` | torch 2.2.2 と依存関係が解決できるバージョン |

## 環境セットアップ手順

```bash
uv python pin 3.12
uv sync
uv run python -m spacy download ja_core_news_trf
```

**分析器**
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])

**匿名化エンジンをインスタンスに**
anonymizer = AnonymizerEngine()


**個人情報識別のカスタマイズはRecognizerクラスをimportして行う**
デフォルトの個人情報識別にカスタマイズできる
- 正規表現/拒否リスト: 固定のパターンに基づく効率的な検出。
- 固有表現認識(NER): 文脈を考慮した機械学習モデルを使用し、高度な検出を実現。NLPエンジン(spaCyやstanza等)を利用。
- カスタムロジック: 特定業務やプロジェクト要件に基づいた独自のルールを適用。
  
EntityRecognizer：Recognizer全体の基底クラス。loadメソッドとanalyzeメソッドが拡張ポイント。
LocalRecognizer：ローカルプロセスで使用されるRecognizer。
PatternRecognizer：正規表現・拒否リストベースのRecognizer。バリデーションや文脈に基づくスコア加算(Context Enhancement)もサポート
RemoteRecognizer：外部サービスを含むリモートプロセスで使用されるRecognizer。

組み込みrecognizer一覧
https://github.com/microsoft/presidio/tree/main/presidio-analyzer/presidio_analyzer/predefined_recognizers





