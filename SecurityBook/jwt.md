画像から読み取れた内容を、できるだけそのまま文字起こししました。影で隠れている部分は一部推測を含み、判読できない箇所は `???` としています。

```text
id-Token（JWT）の検証

1. 署名を確認

方法1

Google の公開鍵をキャッシュした保存
jwks_uri で指定された URL にある

証明書を取得して解析し署名を確認する

（jwt.io のライブラリを使用）

方法2

デバッグ（用途）程度では Google の

tokeninfo エンドポイントを使用
→ 本番運用不可

本番では jwks_uri を使って鍵の URI を
取得できて、鍵を使って tokeninfo を検証する

2. iss クレームの値を確認

3. aud の値が アプリの client-id と
   等しいことを確認

4. exp（有効期限）を確認

5. hd parameter がある場合は一致確認
```

### 補足

このメモは **Google Sign-In / Firebase Authentication の ID Token（JWT）の検証手順**について書かれています。

検証項目としては以下の5点です。

1. **署名（Signature）の検証**
2. **iss（Issuer）の確認**
3. **aud（Audience）が自分の Client ID と一致すること**
4. **exp（Expiration）が有効期限内であること**
5. **hd（Hosted Domain）が必要なら一致すること**

内容としては Google が公開している ID Token 検証手順に沿ったメモになっています。




USER ---------------> userinfo エンドポイント 
                        ↑ userinfo_endpointから取得
                            Google のOIDCディスカバ理ドキュメントを使ってエンドポイントURIを取得する
                            OIDCは複数のエンドポイントを使う必要がある
                        
アクセストークンに 
openid_prifile
email
を含める
Authorizationヘッダーに追加

                            