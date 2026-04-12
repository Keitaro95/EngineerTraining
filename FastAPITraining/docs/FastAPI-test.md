**2.1 推奨されるプロジェクト構造：ミラーリング構成**

テストコードの配置戦略として、最も保守性が高いとされるのが「ミラーリング構成（Mirroring Structure）」である ${1}$。これは、アプリケーションコード（app または src ディレクトリ）の階層構造を、テストディレクトリ（tests）内で完全に模倣する手法です。

**構造例と解説**

project\_root/

├── app/

│ ├── \_\_init\_\_.py

│ ├── main.py \# アプリケーションエントリーポイント

│ ├── api/

│ │ ├── dependencies.py \# 依存性注入定義

│ │ ├── routers/ \# ルーター定義

│ │ └── v1/

│ ├── core/

│ │ ├── config.py \# Pydantic Settings

│ │ └── exceptions.py \# カスタム例外

│ ├── services/ \# ビジネスロジック

│ └── db/ \# データベース関連

├── tests/

│ ├── \_\_init\_\_.py

│ ├── conftest.py \# グローバルフィクスチャ（Sessionスコープ等）

│ ├── unit/ \# 単体テスト

│ │ ├── services/ \# app/servicesに対応

│ │ │ └── test\_auth\_service.py

│ │ └── core/ \# app/coreに対応

│ ├── integration/ \# 統合テスト

│ │ ├── api/ \# app/apiに対応

│ │ │ └── test\_items.py

│ │ └── db/

│ └── performance/ \# パフォーマンステスト（pytest-benchmark）

│ └── test\_latency.py

└── pytest.ini \# pytest設定

**この構造の利点：**

1. **検索性の向上**: `app/services/auth.py` を修正した際、開発者は直感的に `tests/unit/services/test_auth_service.py` を修正すべきであると認識できます。  
2. **スコープの明確化**: 単体テスト（Unit）と統合テスト（Integration）をディレクトリレベルで分離することで、CIパイプラインにおいて「高速な単体テストのみ先に実行する」といった最適化が容易になります。

## 

### **3.1 app.dependency\_overrides のメカニズムと優位性**

従来のPythonテストでは unittest.mock.patch を用いてインポートパスを書き換える手法が一般的であった。しかし、FastAPIにおいては app.dependency\_overrides 属性を使用することが強く推奨される 6。

**patch に対する dependency\_overrides の優位性:**

1. **リファクタリング耐性**: patch は対象の関数がどこでインポートされているか（実装の詳細）に依存する。インポートの場所が変わるとテストが壊れる。対して dependency\_overrides は、依存関数の定義そのものをキーとするため、利用場所が変わってもテストは壊れない。  
2. **スコープの安全性**: dependency\_overrides はFastAPIのDIコンテナレベルでの差し替えであり、グローバルな名前空間を汚染しない。

### **3.2 コンテキストマネージャーによるオーバーライドの安全管理**

app.dependency\_overrides は辞書（dict）であり、テスト終了後にクリーンアップ（キーの削除）を行わないと、後続のテストにモックが残り続ける「テスト汚染」が発生する。これを防ぐため、yield フィクスチャまたはコンテキストマネージャーを用いた管理をチーム標準とすべきである 8。

**推奨実装パターン（フィクスチャファクトリ）:**

Python

\# tests/conftest.py

import pytest  
from fastapi import FastAPI  
from app.main import app as fastapi\_app

@pytest.fixture  
def override\_dependency():  
    """  
    テストケース内で一時的に依存関係をオーバーライドし、自動的に解除するフィクスチャ。  
    """  
    overrides\_to\_restore \= {}

    def \_override(dependency, replacement):  
        overrides\_to\_restore\[dependency\] \= fastapi\_app.dependency\_overrides.get(dependency)  
        fastapi\_app.dependency\_overrides\[dependency\] \= replacement

    yield \_override

    \# テアダウン: 変更された依存関係のみを復元・削除  
    for dep, original in overrides\_to\_restore.items():  
        if original is None:  
            fastapi\_app.dependency\_overrides.pop(dep, None)  
        else:  
            fastapi\_app.dependency\_overrides\[dep\] \= original

### 

## **TestClient / AsyncClient / AsyncMock 使い分けポイント**

TestClient（同期）  
用途: シンプルなエンドポイントのテスト

* await 不要で書きやすい  
* 内部で非同期を同期に変換して実行  
* 単純なCRUD操作の検証に最適

---

AsyncClient（非同期）  
用途: 複雑な非同期処理のテスト

* @pytest.mark.asyncio \+ await で記述  
* 本番と同じ非同期の実行モデルでテスト  
* 必須となるケース:  
  * 並行リクエスト（asyncio.gather）  
  * WebSocket / SSE  
  * タイミング依存のバグ検出

---

AsyncMock  
用途: 非同期関数のモック（代替物）

* async def で定義された依存関係を差し替える  
* await で呼び出せるモックを作成  
* 使う場面:  
  * DBアクセスのモック  
  * 外部APIのモック  
  * タイムアウト/リトライのテスト

---

早見表

| 何をテストする？ | 使うもの |
| :---- | :---- |
| 単純なGET/POST | TestClient |
| 並行処理・WebSocket | AsyncClient |
| DB・外部APIの差し替え | AsyncMock |

---

一言まとめ

* TestClient: 手軽に書きたいとき  
* AsyncClient: 本番と同じ動きを再現したいとき  
* AsyncMock: 非同期の依存を差し替えたいとき

**状況別の推奨選択**

テストを書く  
    │  
    ▼  
外部依存（DB/API）がある？  
    │  
    ├─ YES → AsyncMock で依存をモック  
    │  
    ▼  
非同期処理が複雑？（並行処理/WebSocket/SSE）  
    │  
    ├─ YES → AsyncClient \+ @pytest.mark.asyncio  
    │  
    ├─ NO → TestClient（同期）でOK  
    │  
    ▼  
チームの方針は？  
    │  
    ├─ 統一したい → AsyncClient に統一  
    │  
    └─ シンプルさ優先 → TestClient をベースに

## 2\. with構文を用いた例外処理のテスト

**pytest.raisesによる例外検証:** Pytestではwith pytest.raises(ExceptionType):構文を使って、特定の例外が発生することをテストします。以下は、入力値が不正な場合にValueErrorを送出する関数をテストする例です:

import pytest

def target(x: int):  
    if x \> 100:  
        raise ValueError("不正な値です")  
    return x \* 2

def test\_target\_raises():  
    \# 101を渡すとValueErrorが発生することを検証  
    with pytest.raises(ValueError) as e:  
        target(101)  
    \# 発生した例外メッセージを確認  
    assert str(e.value) \== "不正な値です"

上記のようにpytest.raisesのコンテキストマネージャ内で関数を呼び出し、期待する例外クラスを指定します[\[5\]](https://qiita.com/Jazuma/items/cb8dcd9ff01ed1c2d1f2#:~:text=test_int%20%3D%20101%20,raises%28ValueError%29%20as%20e%3A%20target%28test_int)。e.value経由で例外オブジェクトにアクセスし、メッセージ等も検証可能です。

**例外テストの注意点:** pytest.raises()にはできるだけ具体的な例外クラスを指定します。例えば単にExceptionを指定してしまうと、想定外の例外まで捕捉してしまいテストの意図が曖昧になります[\[6\]](https://qiita.com/Jazuma/items/cb8dcd9ff01ed1c2d1f2#:~:text=)。また、withブロック内では例外発生までのコードのみを書き、**後続のアサーションはブロックの外に出す**必要があります[\[6\]](https://qiita.com/Jazuma/items/cb8dcd9ff01ed1c2d1f2#:~:text=)（上記コードでも、assertはwith文と同じインデントにしている点に注意してください）。

### 

**例外発生をアサート**します:

def test\_service\_raises\_on\_error(mocker):  
    mocker.patch('myapp.service.call\_api', side\_effect=ValueError("bad data"))  
    \# call\_api内でValueErrorが起きた場合、target\_functionもValueErrorをそのまま送出する想定  
    with pytest.raises(ValueError, match="bad data"):  
        target\_function()  \# 内部で call\_api() を呼ぶ関数

上記のようにwith pytest.raises(ValueError)を使うことで、想定した例外が発生することをテストできます[\[3\]](https://zenn.dev/nyanchu/articles/pytest_mock_8da0886bbb9087#:~:text=def%20test_exception_mock%28mocker%29%3A%20mock_func%20%3D%20mocker,raises%28Exception%2C%20match%3D%27mocked%20exception%27%29%3A%20another_function)。

### 

### 

### 

### 

## **FastAPI 異常系テスト設計ガイド**

基本的な考え方  
異常系テストの目的は「エラーが起きたとき、システムが正しく振る舞うか」を検証すること。具体的には：

適切なステータスコードを返しているか  
ユーザーへのメッセージは適切か（詳細すぎない）  
内部ログに詳細が記録されているか  
ステータスコード別テスト設計  
400 Bad Request（ビジネスルール違反）  
発生条件: アプリケーションが明示的に raise HTTPException(400) するケース

def test\_duplicate\_item\_error(client):  
    """重複登録を拒否することを検証"""  
    \# 1回目: 正常登録  
    client.post("/items/", json={"name": "unique\_item"})  
      
    \# 2回目: 同じ名前で登録試行  
    response \= client.post("/items/", json={"name": "unique\_item"})  
      
    assert response.status\_code \== 400  
    assert response.json()\["detail"\] \== "Item already exists"  
401 Unauthorized（認証失敗）  
発生条件: トークンなし、トークン切れ、認証情報不正

def test\_missing\_auth\_token(client):  
    """認証トークンなしでアクセス拒否されることを検証"""  
    response \= client.get("/protected/resource")  
      
    assert response.status\_code \== 401  
    assert response.json()\["detail"\] \== "Not authenticated"

def test\_expired\_token(client):  
    """期限切れトークンが拒否されることを検証"""  
    expired\_token \= "eyJ..."  \# 期限切れトークン  
    response \= client.get(  
        "/protected/resource",  
        headers={"Authorization": f"Bearer {expired\_token}"}  
    )  
      
    assert response.status\_code \== 401  
403 Forbidden（権限不足）  
発生条件: 認証済みだがアクセス権がない

def test\_insufficient\_permissions(client, normal\_user\_token):  
    """一般ユーザーが管理者機能にアクセスできないことを検証"""  
    response \= client.delete(  
        "/admin/users/123",  
        headers={"Authorization": f"Bearer {normal\_user\_token}"}  
    )  
      
    assert response.status\_code \== 403  
    assert response.json()\["detail"\] \== "Not enough permissions"  
404 Not Found（リソース不在）  
発生条件: 指定されたリソースが存在しない

def test\_item\_not\_found(client):  
    """存在しないIDでアクセスした場合を検証"""  
    response \= client.get("/items/99999")  
      
    assert response.status\_code \== 404  
    assert response.json()\["detail"\] \== "Item not found"  
422 Unprocessable Entity（バリデーションエラー）  
発生条件: Pydanticによる入力値検証の失敗（FastAPIが自動生成）

def test\_validation\_error\_missing\_field(client):  
    """必須フィールド欠落時のエラーを検証"""  
    response \= client.post("/items/", json={"price": 100})  \# nameが欠落  
      
    assert response.status\_code \== 422  
    errors \= response.json()\["detail"\]  
      
    \# どのフィールドでエラーが起きたか確認  
    assert any(e\["loc"\] \== \["body", "name"\] for e in errors)  
    assert any(e\["type"\] \== "missing" for e in errors)

def test\_validation\_error\_invalid\_type(client):  
    """型不正時のエラーを検証"""  
    response \= client.post("/items/", json={"name": "test", "price": "not\_a\_number"})  
      
    assert response.status\_code \== 422  
500 Internal Server Error（サーバー内部エラー）  
発生条件: 予期しない例外、DB接続エラーなど

from unittest.mock import MagicMock  
from sqlalchemy.exc import OperationalError

def test\_db\_connection\_error(client, override\_dependency, caplog):  
    """DB接続エラー時の挙動を検証"""  
      
    \# エラーを発生させるモックを作成  
    def raise\_error():  
        raise OperationalError("Connection failed", params=None, orig=None)  
      
    override\_dependency(get\_db, raise\_error)  
      
    response \= client.get("/items/")  
      
    \# ユーザーには汎用メッセージを返す（セキュリティ）  
    assert response.status\_code \== 500  
    assert response.json() \== {"detail": "Internal Server Error"}  
      
    \# 内部ログには詳細が残っている（デバッグ用）  
    assert "Connection failed" in caplog.text  
503 Service Unavailable（サービス利用不可）  
発生条件: 外部サービス障害、メンテナンス中

from unittest.mock import AsyncMock

@pytest.mark.asyncio  
async def test\_external\_api\_unavailable(async\_client, override\_dependency):  
    """外部API障害時の挙動を検証"""  
      
    mock\_api \= AsyncMock()  
    mock\_api.fetch\_data.side\_effect \= TimeoutError("External API timeout")  
      
    override\_dependency(get\_external\_api, lambda: mock\_api)  
      
    response \= await async\_client.get("/data")  
      
    assert response.status\_code \== 503  
    assert "unavailable" in response.json()\["detail"\].lower()  
異常系テストの設計マトリクス  
ステータス	何をテストする	モック必要？  
400	ビジネスルール違反	場合による  
401	認証なし/失敗	トークン生成  
403	権限不足	ユーザー権限  
404	リソース不在	不要  
422	入力値不正	不要  
500	内部エラー	必要（例外発生）  
503	外部障害	必要（タイムアウト）  
重要なポイント  
1\. ユーザーへの情報とログの分離

ユーザーへ: 「Internal Server Error」（詳細を隠す）  
ログへ:    「SQLAlchemy OperationalError: Connection refused...」（詳細を残す）  
2\. 422 と 400 の使い分け  
422: Pydanticが自動で返す（入力形式の問題）  
400: アプリが明示的に返す（ビジネスロジックの問題）  
3\. MagicMock vs AsyncMock  
同期関数のモック: MagicMock \+ side\_effect  
非同期関数のモック: AsyncMock \+ side\_effect

## 

## 

## **6\. LOGとパフォーマンス解析と応答時間の検証**

機能テストがパスしても、応答時間が許容範囲を超えていれば実運用には耐えられない。CIパイプラインの中でパフォーマンスの退行（Performance Regression）を検知する仕組みを組み込む。

### **6.1 ミドルウェアによる簡易レイテンシ計測**

全リクエストの処理時間を計測し、レスポンスヘッダー（X-Process-Time）に付与するミドルウェアは、運用監視だけでなくテスト時の簡易チェックにも有用である 20。

Python

\# app/middleware.py  
import time  
from fastapi import Request

async def add\_process\_time\_header(request: Request, call\_next):  
    start\_time \= time.perf\_counter()  
    response \= await call\_next(request)  
    process\_time \= time.perf\_counter() \- start\_time  
    response.headers \= str(process\_time)  
    return response

**テストコードでのアサーション:**

Python

def test\_api\_latency\_threshold(client):  
    response \= client.get("/fast-endpoint")  
    assert response.status\_code \== 200  
      
    latency \= float(response.headers)  
    \# 閾値判定: ただしCI環境の変動を考慮し、余裕を持たせるかWarning扱いにする  
    assert latency \< 0.5, f"Performance degradation detected: {latency}s"

### **6.2 pytest-benchmark による統計的パフォーマンス解析**

より厳密なパフォーマンス測定には、pytest-benchmark プラグインを導入する 22。これはコードブロックを複数回実行し、平均、最小、最大、標準偏差を算出する。

**特徴と利点:**

* **統計的信頼性**: 1回の実行ではなく、多数回の試行に基づくため、外れ値の影響を排除できる。  
* **比較機能**: 前回のテスト実行結果（ベースライン）と比較し、有意に遅くなった場合のみテストを失敗させる設定が可能。

**実装例:**

Python

def test\_heavy\_computation(benchmark):  
    \# benchmark() は渡された関数を実行し、統計情報を収集する  
    result \= benchmark(heavy\_function, arg1, arg2)  
    assert result \== expected\_output

**チーム運用ルール:**

ベンチマークテストは実行時間が長くなる傾向があるため、通常の開発サイクル（pytest）からは除外し、タグ付け（@pytest.mark.benchmark）を行って、専用のCIジョブやリリース前の負荷テストフェーズで実行するように pytest.ini で制御するのが一般的である。

## 3\. ログ出力の検証方法

**caplogフィクスチャの活用:** pytestにはログ出力を捕捉する組み込みフィクスチャcaplogがあります[\[9\]](https://qiita.com/mag-chang/items/446eeb5f04022eb663f1#:~:text=)。caplogを使うと、テスト中に発生したログメッセージを記録し、内容やレベルを検証できます。たとえば、ある関数がエラー時にロガーにエラーメッセージを出力することをテストするには以下のようにします:

import logging

def function\_under\_test():  
    logger \= logging.getLogger("myapp")  
    logger.error("致命的なエラー発生")

def test\_logs\_error(caplog):  
    \# WARNING以上のログをキャプチャ（デフォルトでWARNING以上が対象）  
    function\_under\_test()  
    \# 指定のエラーログが出力されたか確認  
    assert ("myapp", logging.ERROR, "致命的なエラー発生") in caplog.record\_tuples

上記では、function\_under\_test()内で出力されたERRORレベルのログをcaplog.record\_tuples（タプルのリスト）から検出しています。デフォルトではWARNING以上のログが捕捉されるため、ERRORは自動的に記録されます[\[10\]](https://qiita.com/mag-chang/items/446eeb5f04022eb663f1#:~:text=%E8%81%B7%E5%A0%B4%E3%81%AESlack%E3%81%A7%E5%91%9F%E3%81%84%E3%81%A6%E3%81%BF%E3%81%9F%E3%82%89%20)[\[11\]](https://qiita.com/mag-chang/items/446eeb5f04022eb663f1#:~:text=test)。必要に応じてcaplog.set\_level(logging.INFO)のようにログレベルを下げれば、INFOやDEBUGログもテスト可能です[\[12\]](https://qiita.com/mag-chang/items/446eeb5f04022eb663f1#:~:text=assert%20%28,in%20caplog.record_tuples)。

ログの検証方法は他にもあり、caplog.textで全ログテキストを一括取得して部分文字列マッチすることもできます[\[13\]](https://qiita.com/mag-chang/items/446eeb5f04022eb663f1#:~:text=,%E3%81%93%E3%82%8C%E4%BB%A5%E5%A4%96%E3%81%AB%E3%82%82%E3%80%81%20%60caplog.text%60%20%E3%81%A8%E3%81%99%E3%82%8B%E3%81%A8%E3%80%81%E5%87%BA%E5%8A%9B%E3%81%95%E3%82%8C%E3%81%9F%E3%83%AD%E3%82%B0%E3%82%92str%E3%81%A8%E3%81%97%E3%81%A6%E7%94%9F%E3%81%A7%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B%E3%81%93%E3%81%A8%E3%81%8C%E5%87%BA%E6%9D%A5%E3%81%BE%E3%81%99%E3%80%82)。また、各ログの詳細（logger名、レベル、メッセージ）はcaplog.recordsのリストから取り出せます。上の例では簡便さからrecord\_tuplesでタプル比較をしていますが、より厳密に検証したければany()関数でrecord.levelnameやrecord.getMessage()をチェックする方法もあります。

