---
name: red-from-sample
description: サンプルコードから仕様を言語化し、TDDのREDフェーズ用スケルトンコードを生成します。実装のお手本となるコードがある場合に使用します。
---

# /commands/red-from-sample

実装のお手本にしたいサンプルコードがあります。

TDDのRED CODEを書くために、定義とか仕様だけを言語化して抽出します。このクラスが満たすべき要件（Azureへの接続、音声データの送信、結果の受信）および、名前定義とか、メソッドの数、インタラクション（呼び出し回数）そのものを言語化し、仕様書にします。


さらに言語化を元にスケルトンコードを作成します。
メソッドの中身（処理ロジック）を削除し、pass または return ダミー値 だけにしたコードです。
コメントアウトにはこのクラスが満たすべき要件（Azureへの接続、音声データの送信、結果の受信）および、名前定義とか、メソッドの数、インタラクション（呼び出し回数）を書いてください。これは、red codeの骨組みとなります。


以上、2つのセクションをmdファイルにしましょう。
仕様書　セクション
red codeの骨組みとなるスケルトンコード セクション

## テスト言語化md配置場所

`documents/backend/rag` rag機能に関するテスト言語化md
`documents/backend/speech` speech機能に関するテスト言語化md
`documents/backend/stream` stream機能に関するテスト言語化md
`documents/frontend/officer` 役員画面のテスト言語化md
`documents/frontend/operator` オペレーター画面のテスト言語化md
