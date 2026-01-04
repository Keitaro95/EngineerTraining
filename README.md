****# リポジトリ目的
このリポジトリは、エンジニアリングトレーニングのための
コーディングの筋肉トレーニングです。

## backend環境構築

```
uv python install 3.12
uv python update-shell
uv add -r requirements.txt 
. .venv/bin/activate
uv pip install . // プロジェクト用の仮想環境にpipで現在のディレクトリをインストールする
```
installできない場合
VS CodeでPylanceが正しいPythonインタプリタを参照しているか確認：
- VS Codeを開き、コマンドパレット（Ctrl+Shift+P）を開く。
- Python: Select Interpreterを選択。
- uvで作成した仮想環境のPythonパス（例：.venv/bin/python）を選択

[uvコマンドでinstall](https://zenn.dev/turing_motors/articles/594fbef42a36ee)
[uvエラー解消](https://zenn.dev/manase/scraps/732f5653f87cf4)

### 型チェックmypy
型ヒント（type hints）を使って、型の不一致や型関連のバグをコードを実行せずに検出。大きめの API や型安全性を重視するなら特に強力
```
uv add --dev mypy
```
[tool.mypy]
型定義のない外部パッケージのインポートエラーを無視する設定です（LangChainなど一部ライブラリに型情報が無い場合があります
ignore_missing_imports = True
strict = True
```
型チェック
uv run mypy .
```

### linter
Pylint: Pylint は、Python コードのエラーをチェックし、コーディング標準を適用し、コードの潜在的バグを検出する
高度な構成が可能なオープンソースツールです。Pylint を使用して、特定のユースケース向けのカスタムプラグインを作成することもできます。
```
uv add --dev pylint
pylint --generate-rcfile > .pylintrc
uv run pylint api  # 自作モジュール名（apiディレクトリ）を指定
```
C=Convention, W=Warning, E=Error, R=Refactor, F=Fatal

必要に応じてルールを緩める
プリコミットに組み込むことも可能