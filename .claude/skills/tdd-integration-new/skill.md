---
name: tdd-integration-new
description: テスト駆動開発（TDD）のRed-Green-Refactorサイクルを実施します。対話でテスト対象を絞り込み、コンテキスト消費を最小化します。
---

# TDD 統合テスト（コンテキスト最適化版）

専用のサブエージェントを使用して、厳格なテスト駆動開発のRed-Green-Refactorサイクルを実施します。
**コンテキスト消費を最小化するため、サブエージェントの返却内容を厳しく制限します。**

## フェーズ0: 対話による対象選択（必須）

TDDを開始する前に、以下の3点をユーザーに確認してください：

### 1. テスト仕様書の選択

| 機能 | パス |
|------|------|
| RAG | `documents/backend/rag/` |
| Speech | `documents/backend/speech/` |
| Stream | `documents/backend/stream/` |
| 役員画面 | `documents/frontend/officer/` |
| オペレーター画面 | `documents/frontend/operator/` |

### 2. テスト配置場所の確認

| 機能 | パス |
|------|------|
| RAG | `tests/backend/red-code/rag/test_*.py` |
| Speech | `tests/backend/red-code/speech/test_*.py` |
| Stream | `tests/backend/red-code/stream/test_*.py` |
| 役員画面 | `tests/frontend/red-code/officer/test_*.py` |
| オペレーター画面 | `tests/frontend/red-code/operator/test_*.py` |

### 3. 実装コードの場所の確認

| 機能 | パス |
|------|------|
| RAG | `src/backend/services/rag.py` |
| Speech | `src/backend/services/speech.py` |
| Stream | `src/backend/services/stream.py` |
| オペレーター画面 | `src/frontend/app/pages/1_operator_app.py` |
| 役員画面 | `src/frontend/app/pages/2_officer_app.py` |

**対話例:**
```
どの機能のTDDを実行しますか？
1. RAG (backend)
2. Speech (backend)
3. Stream (backend)
4. 役員画面 (frontend)
5. オペレーター画面 (frontend)
```

選択後、以降のすべてのフェーズは**選択されたディレクトリのみ**を対象とします。

---

## TDDの基本原則

1. テスト仕様書（`documents/`）を読み、テストシナリオを把握する
2. テストリストの中から**ひとつだけ**選び出し、実行可能なテストコードに翻訳する
3. テストが失敗することを確認する（RED）
4. プロダクトコードを変更し、テストを成功させる（GREEN）
5. 必要に応じてリファクタリングを行う（BLUE）
6. テストリストが空になるまで繰り返す

**重要**: ユーザーがテストリストから**1つのテストを選択**し、そのテストに対してのみRED-GREEN-BLUEサイクルを実行します。

---

## フェーズ1: RED - 失敗するテストを書く

🔴 REDフェーズ: `tdd-test-writer-red` サブエージェントに委任

### 入力
- 選択されたテスト仕様書（`documents/{選択パス}/`）
- ユーザーが選択した1つのテストシナリオ
- テスト配置場所（`tests/{選択パス}/`）

### サブエージェントへの指示

**コンテキスト制限（厳守）:**

テスト実行後、以下の情報**のみ**を返してください：

```
---
STATUS: RED_CONFIRMED / RED_FAILED
FILE: tests/xxx/test_yyy.py
TEST_NAME: test_機能名
SUMMARY: 期待通り失敗した理由（1行）
---
```

❌ **禁止事項:**
- テストの全出力ログを返さないこと
- スタックトレースの全文を返さないこと
- pytestの生出力を返さないこと

### 完了条件
テストが失敗することを確認してから次のフェーズへ進む。

---

## フェーズ2: GREEN - テストを通す

🟢 GREENフェーズ: `tdd-implementer-green` サブエージェントに委任

### 入力
- REDフェーズで作成したテストファイルのパス
- 実装対象ファイル（`src/{選択パス}/`）
- **テストファイルと実装ファイルのみ**を読み込む

### サブエージェントへの指示

**スコープ制限:**
- `tests/{選択パス}/` のテストコードのみ参照
- `src/{選択パス}/` の実装コードのみ編集
- 他のディレクトリは一切触れない

**コンテキスト制限（厳守）:**

テスト実行後、以下の情報**のみ**を返してください：

```
---
STATUS: GREEN_CONFIRMED / GREEN_FAILED
FILE: src/xxx/yyy.py
TEST_FILE: tests/xxx/test_yyy.py
CHANGES: 変更内容の要約（1-2行）
---
```

❌ **禁止事項:**
- テストの全出力ログを返さないこと
- スタックトレースの全文を返さないこと
- 実装コードの全文を返さないこと

### 完了条件
テストが成功することを確認してから次のフェーズへ進む。

---

## フェーズ3: BLUE - リファクタリング

🔵 BLUEフェーズ: `tdd-refactorer-blue` サブエージェントに委任

### 入力
- GREENフェーズで編集した実装ファイル（`src/{選択パス}/`）のみ
- 対応するテストファイル（`tests/{選択パス}/`）

### サブエージェントへの指示

**スコープ制限:**
- GREENで変更した`src/`ファイルのみリファクタリング対象
- リファクタリング後、`tests/{選択パス}/`のテストを実行して確認

**コンテキスト制限（厳守）:**

リファクタリング完了後、以下の情報**のみ**を返してください：

```
---
STATUS: REFACTOR_DONE / NO_REFACTOR_NEEDED
FILE: src/xxx/yyy.py
CHANGES: 変更内容（1-2行）または「リファクタリング不要」
REASON: 理由（1行）
TEST_STATUS: PASSED
---
```

❌ **禁止事項:**
- テストの全出力ログを返さないこと
- スタックトレースの全文を返さないこと
- リファクタリング前後のdiffを返さないこと

---

## フェーズ違反

以下を絶対に行わないでください:

- テストより先に実装を書く
- REDの失敗を確認せずにGREENに進む
- BLUE評価をスキップする
- 選択されたディレクトリ以外のファイルを読み書きする
- サブエージェントがログ全文を返す

---

## サイクル完了後

1つのテストに対するRED-GREEN-BLUEサイクルが完了したら：

1. 完了したテストシナリオをユーザーに報告
2. テスト仕様書に新しいシナリオがあれば提示
3. ユーザーが次のテストを選択するか、終了するか確認

**推奨**: 複数テストを連続実行する場合、3-5サイクルごとに `/reset` でコンテキストをクリアすることを推奨します。
