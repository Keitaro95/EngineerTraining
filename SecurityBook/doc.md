以下の内容を整理して、**フロントエンド（Firebase Hosting / React）** と **バックエンド（Cloud Run / FastAPI）** に分けたセキュリティチェックリストとしてまとめました。

```md
# セキュリティチェックリスト

## フロントエンド（Firebase Hosting / React）

### 通信

- [ ] HTTPS を強制している
- [ ] HSTS を有効にしている

---

### セキュリティヘッダー（firebase.json）

- [ ] Content-Security-Policy (CSP) を設定している
- [ ] X-Frame-Options（iframe 対策）
- [ ] X-Content-Type-Options: nosniff
- [ ] Referrer-Policy
- [ ] Permissions-Policy

---

### CSP

- [ ] connect-src を API ドメインのみに制限
- [ ] script-src を必要最小限にする
- [ ] object-src 'none'
- [ ] frame-ancestors を制限

---

### XSS 対策

- [ ] React の標準エスケープを利用
- [ ] dangerouslySetInnerHTML を極力使用しない
- [ ] HTML を表示する場合はサニタイズする

---

### フォーム

- [ ] 入力文字数制限
- [ ] ファイルサイズ制限
- [ ] クライアント側バリデーション

---

### Cookie

- [ ] HttpOnly
- [ ] Secure
- [ ] SameSite

---

### Bot 対策

- [ ] Google reCAPTCHA を導入

---

### 秘密情報

- [ ] APIキーをソースコードへ埋め込まない
- [ ] Secret Manager を利用する

---

## バックエンド（Cloud Run / FastAPI）

### API認証

- [ ] JWT による認証
- [ ] 認証済みユーザーのみ API 利用可能
- [ ] JWT の有効期限を短くする
- [ ] リフレッシュトークンを利用する

---

### 入力値検証

- [ ] Pydantic によるバリデーション
- [ ] 型チェック
- [ ] 異常入力を拒否する

---

### レート制限

- [ ] Rate Limit を実装
- [ ] DoS・総当たり攻撃対策

---

### ファイルアップロード

#### 拡張子

- [ ] 許可拡張子のみ受付

#### MIME Type

- [ ] MIME Type を確認

#### ファイルサイズ

- [ ] 最大サイズを制限

#### バイナリ検査

- [ ] マジックナンバーを確認
- [ ] 拡張子偽装を検出

#### ウイルス対策

- [ ] ウイルススキャン

#### 保存

- [ ] ランダムファイル名へ変更
- [ ] 保存先ディレクトリを制限

---

### 秘密情報

- [ ] Secret Manager を利用
- [ ] 環境変数へ直接書かない

---

## インフラ

### Cloud Run

- [ ] HTTPS のみ
- [ ] IAM を適切に設定
- [ ] 最小権限の原則

---

### ログ

- [ ] エラーログを保存
- [ ] JWT・パスワード等の機密情報はログへ出力しない

---

## 最終チェック

### 認証

- [ ] JWT が漏洩しない設計
- [ ] Cookie の属性を確認
- [ ] API は認証必須

### 通信

- [ ] HTTPS
- [ ] HSTS
- [ ] CSP

### 入力

- [ ] サニタイズ
- [ ] バリデーション
- [ ] ファイル検査

### 攻撃対策

- [ ] XSS
- [ ] Clickjacking
- [ ] MIME Sniffing
- [ ] Bot 対策
- [ ] レート制限
- [ ] DoS 対策

### 秘密情報

- [ ] Secret Manager を利用
- [ ] APIキーを公開していない

### 運用

- [ ] ログ監査
- [ ] エラー監視
- [ ] 定期的な依存ライブラリ更新
```

このまま `docs/security/checklist.md` として管理できる形式になっています。また、OWASP ASVS や OWASP Top 10 に対応する形で項目を追加すると、より実践的なセキュリティチェックリストになります。
