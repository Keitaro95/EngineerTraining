# Streamlit RED CODE 品質基準

> Claude Code Subagent向け：Playwright MCPによるStreamlit TDDのREDフェーズ評価基準

---

## 概要

本ドキュメントは、Streamlit アプリケーションのTDD開発において、REDフェーズ（失敗するテストを書く段階）のコード品質を評価・リファクタリングするための基準を定義する。

### 前提条件

- テストフレームワーク: Playwright (pytest-playwright)
- セレクタ戦略: ARIA / Role ベース優先
- 対象: Streamlit UIコンポーネント + バックエンドイベント

---

## 1. セレクタ品質基準

### 1.1 セレクタ優先順位（必須遵守）

| 優先度 | セレクタ種別 | 例 | 使用条件 |
|--------|-------------|-----|----------|
| 1 | `get_by_role()` | `get_by_role("button", name="送信")` | **最優先** |
| 2 | `get_by_label()` | `get_by_label("ユーザー名")` | フォーム要素 |
| 3 | `get_by_text()` | `get_by_text("登録完了")` | 表示テキスト確認 |
| 4 | `get_by_test_id()` | `get_by_test_id("result-panel")` | ARIA不可時 |
| 5 | `locator(css)` | `locator('[data-testid="stSidebar"]')` | **最終手段のみ** |

### 1.2 セレクタ禁止事項

```python
# ❌ 禁止: Streamlit内部クラス名への直接依存
page.locator("div.stButton > button")
page.locator(".stTextInput input")
page.locator("div.element-container")

# ❌ 禁止: 脆いXPath
page.locator("//div[3]/button[1]")

# ✅ 許可: ARIAベース
page.get_by_role("button", name="計算実行")
page.get_by_label("入力値")
```

### 1.3 セレクタ品質チェックリスト

- [ ] Streamlit内部クラス（`.st*`）を直接参照していない
- [ ] XPathを使用していない（または最小限）
- [ ] `get_by_role()` または `get_by_label()` を優先使用
- [ ] `data-testid` 使用時は実装側への要求として明記

---

## 2. テスト構造基準

### 2.1 テスト命名規則

```python
# ✅ 良い例: 「〜した場合、〜すべき」形式
def test_送信ボタンクリック時_結果が表示されるべき(page):
def test_無効な入力の場合_エラーメッセージが表示されるべき(page):
def test_operator_button_click_should_display_result(page):

# ❌ 悪い例: 曖昧な命名
def test_button(page):
def test_ui(page):
def test_1(page):
```

### 2.2 テスト分類（必須明記）

各テストファイルの先頭に分類を明記すること：

```python
"""
テスト分類: UI検証
対象コンポーネント: 計算ボタン
期待するHTML構造: <button aria-label="計算実行">計算実行</button>
"""
```

| 分類 | 目的 | 検証対象 |
|------|------|----------|
| UI検証 | 要素の存在・表示確認 | `to_be_visible()`, `to_have_count()` |
| イベント検証 | ユーザー操作の結果確認 | クリック後の状態変化 |
| API検証 | バックエンド連携確認 | `expect_response()` |
| 状態検証 | session_state変化確認 | 状態遷移 |

### 2.3 1テスト1検証の原則

```python
# ✅ 良い例: 単一の振る舞いを検証
def test_送信ボタンが表示される(page):
    page.goto("http://localhost:8501")
    expect(page.get_by_role("button", name="送信")).to_be_visible()

def test_送信ボタンクリックで結果表示(page):
    page.goto("http://localhost:8501")
    page.get_by_role("button", name="送信").click()
    expect(page.get_by_test_id("result")).to_be_visible()

# ❌ 悪い例: 複数の振る舞いを1テストに詰め込み
def test_送信フロー全体(page):
    page.goto("http://localhost:8501")
    expect(page.get_by_role("button", name="送信")).to_be_visible()  # 検証1
    page.get_by_role("button", name="送信").click()
    expect(page.get_by_test_id("result")).to_be_visible()  # 検証2
    expect(page.get_by_text("成功")).to_be_visible()  # 検証3
```

---

## 3. RED フェーズ必須要件

### 3.1 実装前失敗の保証

REDテストは、対応する実装がない状態で**必ず失敗**しなければならない。

```python
# このテストが通る = 実装が既に存在する = REDではない
def test_未実装機能のボタンが存在する(page):
    page.goto("http://localhost:8501")
    # この時点でボタンが存在しないことを確認済みであること
    expect(page.get_by_role("button", name="新機能")).to_be_visible()
```

### 3.2 失敗理由の明確性

テストが失敗する理由が明確であること：

```python
# ✅ 良い例: 失敗理由が明確
def test_計算結果が表示される(page):
    """
    失敗理由: result-panelコンポーネントが未実装
    期待: data-testid="result-panel" を持つ要素が表示される
    """
    page.goto("http://localhost:8501")
    page.get_by_role("button", name="計算").click()
    expect(page.get_by_test_id("result-panel")).to_be_visible()
```

### 3.3 入力と期待出力の明示

```python
def test_数値入力後の計算結果(page):
    """
    入力: 数値フィールドに "42" を入力
    操作: 計算ボタンをクリック
    期待出力: "結果: 84" が表示される
    """
    page.goto("http://localhost:8501")
    page.get_by_label("数値").fill("42")
    page.get_by_role("button", name="計算").click()
    expect(page.get_by_text("結果: 84")).to_be_visible()
```

---

## 4. Streamlit固有の検証パターン

### 4.1 UI検証パターン

```python
from playwright.sync_api import expect

def test_サイドバーが表示される(page):
    page.goto("http://localhost:8501")
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()

def test_ボタンが2つ存在する(page):
    page.goto("http://localhost:8501")
    expect(page.get_by_role("button")).to_have_count(2)

def test_タイトルが正しい(page):
    page.goto("http://localhost:8501")
    expect(page.get_by_role("heading", name="アプリタイトル")).to_be_visible()
```

### 4.2 イベント検証パターン

```python
from playwright.sync_api import expect

def test_operatorボタンがバックエンドを呼び出す(page):
    page.goto("http://localhost:8501")
    
    # API呼び出しを監視
    with page.expect_response(
        lambda r: "/api/operator" in r.url and r.status == 200
    ):
        page.get_by_role("button", name="operator").click()
    
    # UI更新の確認
    expect(page.get_by_test_id("operator-result")).to_be_visible()

def test_フォーム送信後にメッセージ表示(page):
    page.goto("http://localhost:8501")
    
    page.get_by_label("名前").fill("テスト太郎")
    page.get_by_role("button", name="送信").click()
    
    # Streamlitのリランを待つ
    expect(page.get_by_text("こんにちは、テスト太郎さん")).to_be_visible()
```

### 4.3 状態検証パターン（session_state）

```python
def test_カウンター増加(page):
    """
    検証対象: st.session_state.counter の増加
    表示要素経由で間接的に検証
    """
    page.goto("http://localhost:8501")
    
    # 初期状態
    expect(page.get_by_test_id("counter-display")).to_have_text("0")
    
    # 操作
    page.get_by_role("button", name="増加").click()
    
    # 状態変化（UIを通じて検証）
    expect(page.get_by_test_id("counter-display")).to_have_text("1")
```

---

## 5. 品質評価チェックリスト

### 5.1 構造品質（必須）

- [ ] テスト名が仕様を表現している（「〜した場合、〜すべき」形式）
- [ ] 1テストで検証する振る舞いは1つのみ
- [ ] テスト分類（UI/イベント/API/状態）が明記されている
- [ ] 入力と期待出力がdocstringまたはコメントで明示

### 5.2 セレクタ品質（必須）

- [ ] `get_by_role()` または `get_by_label()` を優先使用
- [ ] Streamlit内部クラス（`.st*`）への直接依存なし
- [ ] `data-testid` 使用時は実装要求として文書化
- [ ] XPath未使用（または最小限かつ理由明記）

### 5.3 REDフェーズ品質（必須）

- [ ] 実装が空/未存在なら必ずFAILする
- [ ] 失敗理由がテストコードから読み取れる
- [ ] 期待するHTML/ARIA構造が明確

### 5.4 Streamlit固有品質（推奨）

- [ ] `page.goto()` の後に適切な待機処理
- [ ] session_state検証はUI要素経由
- [ ] API検証は `expect_response()` 使用
- [ ] リラン（再実行）を考慮した設計



### 6.1 documents ↔ tests 対応

```
documents/frontend/calculator/spec.md
    ↓ 対応
tests/frontend/calculator/test_calculator.py
```

| チェック項目 | 確認方法 |
|-------------|----------|
| 仕様に対応するテストが存在するか | ファイル名の一致 |
| テストが仕様の意図を反映しているか | docstringと仕様の照合 |
| 仕様の各要件にテストがあるか | チェックリスト |

### 6.2 tests ↔ src 対応

```
tests/frontend/calculator/test_calculator.py
    ↓ 対応
src/frontend/calculator/calculator.py
```

| チェック項目 | 確認方法 |
|-------------|----------|
| テストに対応する実装ファイルが特定できるか | パス構造の一致 |
| 過剰なテスト（実装不要）がないか | カバレッジ逆引き |
| 不足しているテストがないか | 仕様との差分 |

### 6.3 ミラー構造の例

```
documents/
└── frontend/
    ├── calculator/
    │   └── spec.md          # 計算機能の仕様
    ├── auth/
    │   └── login.spec.md    # ログイン仕様
    └── dashboard/
        └── spec.md          # ダッシュボード仕様

tests/
└── frontend/
    ├── calculator/
    │   └── test_calculator.py
    ├── auth/
    │   └── test_login.py
    └── dashboard/
        └── test_dashboard.py

src/
└── frontend/
    ├── calculator/
    │   └── calculator.py
    ├── auth/
    │   └── login.py
    └── dashboard/
        └── dashboard.py
```

### 6.4 濾過チェックリスト

- [ ] `documents/frontend/X/` に対応する `tests/frontend/X/` が存在する
- [ ] `tests/frontend/X/` に対応する `src/frontend/X/` が存在する（GREEN後）
- [ ] 孤立したテスト（仕様なし）がない
- [ ] 孤立した仕様（テストなし）がない

### 6.5 RED品質スコアリング

| 基準 | 配点 | 評価方法 |
|------|------|----------|
| セレクタ品質 | 30点 | ARIA優先度遵守 |
| テスト構造 | 25点 | 命名・分類・単一責任 |
| RED保証 | 25点 | 未実装時の失敗確認 |
| ドキュメント | 20点 | 入出力・期待構造の明記 |

**合格ライン: 70点以上**

---

## 7. 期待するHTML/ARIA構造の文書化

REDテストを書く際、実装側に要求するHTML構造を明記する：

```python
def test_計算ボタンが存在する(page):
    """
    期待するHTML構造:
    <button aria-label="計算実行" data-testid="calc-button">
        計算実行
    </button>
    
    Streamlit実装例:
    st.button("計算実行", key="calc-button")
    
    注意: Streamlitは自動的にボタンテキストをaria-labelとして使用
    """
    page.goto("http://localhost:8501")
    expect(page.get_by_role("button", name="計算実行")).to_be_visible()
```

---

## 8. Streamlit コンポーネント → セレクタ対応表

| Streamlit API | 推奨セレクタ | 備考 |
|--------------|-------------|------|
| `st.button("X")` | `get_by_role("button", name="X")` | テキストがname |
| `st.text_input("Y")` | `get_by_label("Y")` | ラベルで取得 |
| `st.selectbox("Z", [...])` | `get_by_label("Z")` + `select_option()` | |
| `st.checkbox("W")` | `get_by_role("checkbox", name="W")` | |
| `st.slider("S", ...)` | `get_by_role("slider", name="S")` | |
| `st.sidebar` | `locator('[data-testid="stSidebar"]')` | 例外的にCSS |
| カスタム要素 | `get_by_test_id("xxx")` | key属性を活用 |

---

## 付録: テンプレート

### A. UIテストテンプレート

```python
"""
テスト分類: UI検証
対象: {コンポーネント名}
期待HTML: {期待する構造}
"""
from playwright.sync_api import expect

def test_{対象}_{状態}_{期待}(page):
    """
    入力: なし
    期待出力: {要素}が{状態}
    失敗理由: {コンポーネント}が未実装
    """
    page.goto("http://localhost:8501")
    expect(page.get_by_role("{role}", name="{name}")).to_be_visible()
```

### B. イベントテストテンプレート

```python
"""
テスト分類: イベント検証
対象: {操作名}
API: {エンドポイント}（該当する場合）
"""
from playwright.sync_api import expect

def test_{操作}_{結果}(page):
    """
    入力: {入力値}
    操作: {ユーザー操作}
    期待出力: {結果}
    失敗理由: {機能}が未実装
    """
    page.goto("http://localhost:8501")
    
    # 操作
    page.get_by_role("{role}", name="{name}").click()
    
    # 検証
    expect(page.get_by_text("{期待テキスト}")).to_be_visible()
```

---

## 9. UI仕様YAML構造（ページ単位）

各ページに `ui/` ディレクトリを配置し、以下の3ファイルでUI仕様を定義している。
該当するyamlを採用して、TDDのREDフェーズを実装すること

### 9.1 ディレクトリ構造

```
documents/frontend/app/pages/{page_name}/ui/
├── ui-structure.aria.yaml   # DOMコンテンツのレイアウト仕様
├── ui.constraints.yaml      # CSS幅・サイズ等の制約仕様
└── interactions.yaml        # イベント仕様（クリック→結果）
```

### 9.6 使用例：officerページ

```
documents/frontend/app/pages/officer/ui/
├── ui-structure.aria.yaml
├── ui.constraints.yaml
└── interactions.yaml
```

この仕様に基づき、テストを作成：

```python
# tests/frontend/app/pages/officer/test_officer.py
def test_サイドバーが表示される(page):
    """ui-structure.aria.yaml: sidebar.visible = true"""
    page.goto("http://localhost:8501/officer")
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()

def test_ボタンが2つ存在する(page):
    """ui-structure.aria.yaml: buttons.count = 2"""
    page.goto("http://localhost:8501/officer")
    expect(page.get_by_role("button")).to_have_count(2)

def test_operatorボタンクリックでAPIが呼ばれる(page):
    """interactions.yaml: operator_button_click"""
    page.goto("http://localhost:8501/officer")
    with page.expect_response(
        lambda r: "/api/operator" in r.url and r.status == 200
    ):
        page.get_by_role("button", name="operator").click()
```

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2025-01-27 | 初版作成 |
| 2025-01-27 | UI仕様YAML構造（セクション9）追加 |
