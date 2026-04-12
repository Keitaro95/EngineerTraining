


セクション7: OAuth2 + JWT認証のフロントエンド(TypeScript)連携
OAuth2PasswordBearerのtokenUrlパラメータの意味
OAuth2PasswordBearer(tokenUrl="token")のtokenUrlは、クライアントがユーザー名とパスワードを送信してトークンを取得するエンドポイントのURLを指定する（https://fastapi.tiangolo.com/tutorial/security/first-steps/ ）。この値はOpenAPIスキーマのsecuritySchemesに書き込まれ、Swagger UIの「Authorize」ボタンがこのURLにPOSTリクエストを送る。

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# → Swagger UIに「Authorize」ボタンが表示され、/tokenにPOSTする

依存関係として使用されると、AuthorizationヘッダーからBearerトークンを抽出し、存在しない場合は401を返す。OAuth2はフォームデータ（JSONではない）でユーザー名/パスワードを送信するため、python-multipartパッケージが必要だ。
JWT トークンの生成・検証フロー
公式チュートリアル（https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ ）は現在PyJWT + pwdlibを使用している（旧python-jose + passlibから移行）。


import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()  # Argon2をデフォルト使用
# トークン生成
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# トークン検証（依存関係として使用）
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

補足情報：使用ライブラリ

このフローは、FastAPIの公式チュートリアルで推奨されている新しい構成に従い、JWTの操作にPyJWTを、パスワードのハッシュ化にpwdlib（Argon2idを使用）を使用しています。

なお、トークン検証関数
get_current_user
は、
oauth2_scheme
（
OAuth2PasswordBearer
）の依存関係により
Authorization
ヘッダーからBearerトークンが抽出された後に実行され、検証失敗時には401エラーを返すように設計されています。

フロントエンド(TypeScript)からのログインフロー



// Axiosインターセプターでの自動トークン付与とリフレッシュ：
import axios from "axios";
const apiClient = axios.create({ baseURL: "http://localhost:8000" });

// リクエスト時にBearerトークンを自動付与
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 401時にリフレッシュトークンで自動更新
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      const res = await axios.post("/refresh", { refresh_token: refreshToken });
      localStorage.setItem("access_token", res.data.access_token);
      originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
      return apiClient(originalRequest);
    }
    return Promise.reject(error);
  }
);



補足情報：トークン保存とリフレッシュフロー
ログインフロー: トークン取得時、データはJSONではなく application/x-www-form-urlencoded 形式で送信されます。
トークン保存推奨: アクセストークンはXSSリスクが低いReactのメモリ（state/context）に、リフレッシュトークンはHttpOnly, Secure, SameSite=Strict属性付きのCookieに格納することが推奨されています。
インターセプター: Axiosインターセプターは、リクエストごとに Authorization ヘッダーを自動で付与し、401エラー発生時にはリフレッシュトークンを使ってアクセストークンの自動更新を試みるための仕組みです。


トークン保存先の推奨は、**アクセストークンをReactのメモリ（state/context）**に、リフレッシュトークンをHttpOnly, Secure, SameSite=StrictCookieに格納するパターンだ。localStorageはXSS脆弱性（JavaScriptから読み取り可能）、Cookieは CSRF脆弱性（自動送信される）があるため、両方の長所を組み合わせる。
pydantic-settings による環境変数管理
承知いたしました。ご提示いただいた
pydantic-settings
による環境変数管理の設定コードから空行を削除し、整形しました。これは、
@lru_cache
を利用して設定をシングルトン化するパターンです。
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env")
@lru_cache
def get_settings():
    return Settings()
補足情報：シングルトン化（@lru_cache）

ドキュメントによると、
@lru_cache
は、.envファイルの読み込みをリクエストごとに繰り返さないためのシングルトン化（一度だけ実行し、結果をキャッシュする）に役立ちます。

ただし、
@lru_cache
はコルーチンオブジェクトがキャッシュされてしまうため、async def関数には使えないという制約があります。そのため、必ず通常の
def
で定義する必要があります。


優先順位（高→低）：初期化時引数 > OS環境変数 > .envファイル > デフォルト値。@lru_cacheは.envファイルの読み込みをリクエストごとに繰り返さないためのシングルトン化で、テスト時はget_settings.cache_clear()でリセットするか、app.dependency_overrides[get_settings]でオーバーライドする。@lru_cacheはasync def関数には使えない（コルーチンオブジェクトがキャッシュされてしまう）ため、必ず通常のdefで定義する。
pwdlib によるパスワードハッシュ
passlibはPython 3.13でcryptモジュール削除により動作しなくなる。後継のpwdlib（FastAPI Usersの作者が開発）が公式推奨に変更された。

# pip install "pwdlib[argon2]"
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()  # Argon2idを使用
hashed = password_hash.hash("mysecretpassword")
is_valid = password_hash.verify("mysecretpassword", hashed)
secrets.compare_digest() によるタイミング攻撃対策
通常の文字列比較==は最初の不一致文字で即座にFalseを返すため、応答時間の差異から攻撃者が1文字ずつ認証情報を推測できる。secrets.compare_digest()は全バイトを常に比較し、一致/不一致に関わらず同一時間で完了する（https://fastapi.tiangolo.com/advanced/security/http-basic-auth/ ）。

承知いたしました。ご提示いただいたsecrets.compare_digest()によるタイミング攻撃対策のコードスニペットから空行を削除し、整形しました。
import secrets
# ✅ タイミング攻撃に対して安全
is_correct = secrets.compare_digest(
    credentials.username.encode("utf8"),
    b"correct_username",
)
# 必ず両方の比較を行ってから判定する（短絡評価を避ける）
if not (is_correct_username and is_correct_password):
    raise HTTPException(status_code=401)
補足情報：タイミング攻撃対策

secrets.compare_digest()は、通常の文字列比較（==）が最初の不一致文字で即座に終了する（短絡評価）ことによる応答時間の差異を利用したタイミング攻撃を防ぐために使用されます。
この関数は全バイトを常に比較し、一致/不一致に関わらず同一時間で完了することを保証します。
APIキーの比較、webhook署名検証、またはHTTP Basic認証など、機密性の高い認証情報を比較する際に不可欠です。
ただし、bcryptやArgon2を用いたパスワード検証、またはJWT署名検証は、既に内部で定時間比較を行っているため、この関数を適用する必要はありません。


APIキー比較、webhook署名検証、HTTP Basic認証で使用する。bcrypt/argon2のパスワード検証やJWT署名検証は内部的に既に定時間比較を行っているため不要だ。

