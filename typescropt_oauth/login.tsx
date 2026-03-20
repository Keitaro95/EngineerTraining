
// ts token取得
// OAuth2パスワードフローでは**application/x-www-form-urlencoded形式でトークンを取得する。これはJSON送信ではない**点に注意が必要だ。

export interface TokenResponse {
    access_token: string
}


async function Login(username: string, password: string): Promise<TokenResponse> {
    // bodyに入る paramsを丸める
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    // POSTで送る
    const response = await fetch("http://localhost:8000/token", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: params.toString(),
    })
    if (!response.ok) throw new Error(`Login failed: ${response.status}`);
    const data: TokenResponse = await response.json();
    localStorage.setItem("access_token", data.access_token);
    return data;
}


// === 認証済みリクエスト ===
// FastAPIバックエンドの /users/me エンドポイントと連携し、ログイン中のユーザー自身の情報を取得するための関数です。
async function fetchCurrentUser(): Promise<User> {
  const token = localStorage.getItem("access_token");
  const response = await fetch("http://localhost:8000/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.json();
}
