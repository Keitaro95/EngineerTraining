---
name: frontend-yaml-writer
invocation: frontend-yaml-writer
description: HTML/CSS/JSのサンプルファイルからStreamlit UI仕様YAMLを生成するスキル
tags: [frontend, yaml, ui, streamlit]
isUserInvocable: true
---

# Frontend YAML Writer Skill

HTML/CSS/JSのサンプルファイルを読み込んで、Streamlit向けUI仕様YAMLを生成します。

## 実行手順

1. **ユーザーにサンプルHTMLファイルのパスを要求する**
   - AskUserQuestion ツールを使って、対話的にHTMLファイルのパスを尋ねる
   - ユーザーが提供したパスを使って Read ツールでHTMLファイルを読み込む
   - レイアウト・UI要素・イベント情報を抽出します

2. **2つのYAMLファイルを生成**
   - レイアウト・UI仕様: `documents/frontend/app/pages/{page_name}/ui/ui-contract.yaml`
   - イベント・クリック・ロジック: `documents/frontend/app/pages/{page_name}/ui/interactions.yaml`

## ディレクトリ構造

```
documents/frontend/app/pages/{page_name}/ui/
├── ui-contract.yaml      # レイアウト・UI仕様（ARIA構造 + CSS制約）
└── interactions.yaml     # イベント仕様（クリック→結果）
```

## ui-contract.yaml（レイアウト・UI仕様）

UIの構造・存在・表示状態とCSS制約を統合的に定義します。

```yaml
# UI Contract: Layout & Components
sidebar:
  testid: stSidebar
  visible: true
  width: 300px
  min-width: 250px
  max-width: 350px

buttons:
  count: 2
  items:
    - testid: operatorButton
      label: "Operator"
      height: 38px
      min-width: 100px
    - testid: submitButton
      label: "Submit"
      height: 38px
      min-width: 100px

main_content:
  testid: mainContent
  role: region
  margin-left: 300px
  padding: 16px
```

## interactions.yaml（イベント仕様）

ユーザー操作と期待される結果をWhen/Then形式で定義します。

```yaml
# Interaction Specifications
- interaction: operator_button_click
  when:
    - operator ボタンをクリックする
  then:
    - FastAPI の /api/operator が呼ばれる
    - ステータス 200 を返す
    - 結果が画面に表示される

- interaction: submit_button_click
  when:
    - フォームに入力後、送信ボタンをクリックする
  then:
    - 入力値がバリデーションされる
    - 成功時はメッセージが表示される
```

## YAML生成時の注意点

- HTMLから要素を抽出する際は、testid, role, label等のARIA属性を優先的に取得
- CSS制約は崩れ防止のため、具体的なpx値を記載
- イベント仕様は、操作の流れを明確にするため、When/Then形式で記述
- Streamlit特有のコンポーネント（st.sidebar, st.button等）への変換を考慮
