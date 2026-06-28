DB

Cloud SQL for mysql

パブリックIPをわけない
プライベートIPを
最小限のIPアドレスのみ許可

SSL 必須 require-ssl

backend － Cloud SQL

sql/client
証明書パス　　　サーバー証明書

DB
DBアカウント　強力パスワード

IAM認証で DB接続用サービスアカウント

Secret Managerで

Userパスワードのハッシュ化

自動バックアップ


＜全体＞

Cloud Armor
WAF

ファイアウォール
レートリミット
DDoS
ブルートフォース
WAFルール
攻撃パターン検知

　　　　LB
　　　HTTPS

Cloud Run

Ingress
内部のみ
ロードバランサ

コンテナ脆弱性スキャン

デプロイ前の検査

gcloud artifacts docker images
list --occurrences

ライブラリアップデート
セキュリティアップデート
SBOM管理