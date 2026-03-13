---
name: img-to-htmlcss
description: |
  PNG、JPG、スクリーンショット等の画像ファイルからUIレイアウトを詳細に言語化するスキルです。
  画面上の配置、カラースキーム、コンポーネント構成、スペーシングを解析し、
  開発者がそのままコーディングに使える形式で出力します。
  Streamlit向けの実装ヒントも含めて提供します。
invocation:
  - /img-to-htmlcss
  - /ui-to-code
input:
  - 画像ファイルパス（PNG、JPG、JPEG、GIF、WebP等）
  - クリップボードからのスクリーンショット
output:
  - UIレイアウトの詳細な解析
  - 再現用HTML/CSSコード
  - Streamlit実装コード例（オプション）
---

# Image to HTML/CSS UI Reproducer Skill

## 概要

画像からUIを解析し、そのまま使用できるHTML/CSSコードを生成します。

## Instructions

### 1. 画像の読み取り

ユーザーから提供された画像を Read ツールで読み取ります。

```
Read tool で画像ファイルを読み込む
```

### 2. UI解析と再現コード生成

画像を解析し、以下の順序で処理を行います：

1. レイアウト構造の把握
2. カラー・スタイルの抽出
3. HTML/CSSコードの生成

---

## 出力フォーマット

### 📐 レイアウト解析（Layout Analysis）

```
- 画面サイズ/アスペクト比の推定
- レイアウトパターン（Flexbox / Grid / 固定幅等）
- 主要セクションの構成
```

### 🎨 デザイントークン（Design Tokens）

```css
:root {
  /* Colors */
  --color-background: #XXXXXX;
  --color-primary: #XXXXXX;
  --color-secondary: #XXXXXX;
  --color-text: #XXXXXX;
  --color-accent: #XXXXXX;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Typography */
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 32px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}
```

### 🏗️ HTML構造（HTML Structure）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UI Reproduction</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- 画像から解析した構造をここに出力 -->
  <header class="header">
    <!-- ヘッダー要素 -->
  </header>

  <main class="main">
    <!-- メインコンテンツ -->
  </main>

  <footer class="footer">
    <!-- フッター要素 -->
  </footer>
</body>
</html>
```

### 🎯 CSSスタイル（CSS Styles）

```css
/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.5;
}

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* 各コンポーネントのスタイルを画像から解析して出力 */

/* Header */
.header {
  /* 解析結果に基づくスタイル */
}

/* Main Content */
.main {
  /* 解析結果に基づくスタイル */
}

/* Components */
.card {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
}

.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  opacity: 0.9;
}
```

### 📱 レスポンシブ対応（Responsive Styles）

```css
/* Tablet */
@media (max-width: 768px) {
  /* タブレット向け調整 */
}

/* Mobile */
@media (max-width: 480px) {
  /* モバイル向け調整 */
}
```

### 🐍 Streamlit実装（オプション）

Streamlitで実装する場合のコード例：

```python
import streamlit as st

st.set_page_config(
    page_title="App Title",
    page_icon="🎨",
    layout="wide"  # or "centered"
)

# カスタムCSS注入
st.markdown("""
<style>
    /* 上記CSSをここに挿入 */
    .stApp {
        background-color: var(--color-background);
    }
</style>
""", unsafe_allow_html=True)

# レイアウト実装
with st.sidebar:
    st.title("Navigation")
    # サイドバー要素

# メインコンテンツ
st.title("Page Title")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Label", "Value")
# ...
```

---

## 解析時のガイドライン

### 色の抽出

- 背景色、テキスト色、アクセント色を正確に抽出
- グラデーションがある場合は方向と色停止点を記述
- 透明度（opacity）も考慮

### レイアウトの判定

| パターン | 判定基準 | CSS実装 |
|---------|---------|---------|
| 横並び | 要素が水平に配置 | `display: flex` |
| グリッド | 格子状の配置 | `display: grid` |
| 中央寄せ | コンテンツが中央 | `margin: 0 auto` or `justify-content: center` |
| サイドバー | 固定幅のサイド領域 | `grid-template-columns: 250px 1fr` |

### コンポーネントの識別

- **ボタン**: クリック可能な要素、角丸、背景色あり
- **カード**: 囲み、影、パディングのある要素
- **フォーム**: 入力フィールド、ラベル、送信ボタン
- **ナビゲーション**: リンクのリスト、アイコン付き
- **テーブル**: 行と列のデータ表示

### 数値の推定

- スペーシングは8の倍数を基準（8px, 16px, 24px, 32px）
- フォントサイズは標準的な値を使用（12, 14, 16, 18, 24, 32px）
- 角丸は4, 8, 12, 16pxのいずれかで推定

---

## 出力例

### 入力: ダッシュボード画像

```
📐 レイアウト解析

- 推定サイズ: 1440px x 900px（デスクトップ）
- レイアウト: サイドバー（240px固定）+ メインエリア（残り）
- 構成: ヘッダー、サイドナビ、メトリクスカード群、グラフエリア
```

```html
<!-- dashboard.html -->
<div class="dashboard">
  <aside class="sidebar">
    <div class="logo">
      <img src="logo.svg" alt="Logo">
    </div>
    <nav class="nav">
      <a href="#" class="nav-item active">
        <span class="icon">📊</span>
        <span>Dashboard</span>
      </a>
      <a href="#" class="nav-item">
        <span class="icon">📈</span>
        <span>Analytics</span>
      </a>
    </nav>
  </aside>

  <main class="main-content">
    <header class="page-header">
      <h1>Dashboard</h1>
      <div class="search-bar">
        <input type="text" placeholder="Search...">
      </div>
    </header>

    <section class="metrics">
      <div class="metric-card">
        <span class="metric-label">Total Users</span>
        <span class="metric-value">12,345</span>
        <span class="metric-change positive">+12%</span>
      </div>
      <!-- 他のカード -->
    </section>
  </main>
</div>
```

```css
/* dashboard.css */
:root {
  --sidebar-width: 240px;
  --color-sidebar-bg: #1a1a2e;
  --color-main-bg: #f5f5f5;
  --color-card-bg: #ffffff;
  --color-primary: #4f46e5;
  --color-text: #1f2937;
  --color-text-muted: #6b7280;
  --color-positive: #10b981;
}

.dashboard {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

.sidebar {
  background-color: var(--color-sidebar-bg);
  padding: 24px 16px;
  color: white;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover,
.nav-item.active {
  background-color: rgba(255,255,255,0.1);
  color: white;
}

.main-content {
  background-color: var(--color-main-bg);
  padding: 24px 32px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.metric-card {
  background: var(--color-card-bg);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text);
}

.metric-change.positive {
  color: var(--color-positive);
}
```

---

## エラーハンドリング

| 状況 | 対応 |
|-----|-----|
| 画像が不鮮明 | 読み取れる範囲で実装し、不明箇所は`/* TODO: 要確認 */`で明示 |
| 複雑すぎるUI | 主要コンポーネントを優先、詳細は段階的に追加 |
| 特殊なアニメーション | 静的な状態を実装し、アニメーションは別途コメントで説明 |
| カスタムフォント | システムフォントで代替、フォント名をコメントに記載 |

## 注意事項

1. **セマンティックHTML**: 適切なHTML5要素を使用（`header`, `nav`, `main`, `section`, `article`等）
2. **アクセシビリティ**: `alt`属性、適切なコントラスト比、フォーカス状態を考慮
3. **パフォーマンス**: 不要なネストを避け、効率的なセレクタを使用
4. **保守性**: CSS変数を活用し、値のハードコードを最小限に
