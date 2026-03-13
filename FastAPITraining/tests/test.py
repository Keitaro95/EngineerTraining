# コード内の各行が「何のためにあるのか」「どう動くのか」を詳しくコメントで解説しました。
# これを読むだけで、フィクスチャの仕組み（準備 → 実行 → 後片付け）が理解できるようにしています。

# Python


import sys
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# =================================================================
# 1. Azureサービスのモック化 (自動実行)
# =================================================================
@pytest.fixture(scope="function", autouse=True)
def mock_azure_services():
    """
    Azure SDKをモック化（偽装）するフィクスチャ。
    
    【ポイント】
    - scope="function": テスト関数が1つ実行されるたびにリセットされる（常に新品の状態）。
    - autouse=True  : テスト関数側で引数に書かなくても、勝手に自動で実行される。
                      これにより「うっかりモックし忘れて課金された！」を防ぐ。
    """
    # --- [前準備: Setup] ---

    # 1. 偽物のオブジェクト(MagicMock)を作る
    # MagicMockは、どんなメソッドを呼び出してもエラーにならず、とりあえず成功したフリをしてくれる便利な奴。
    mock_speech = MagicMock()
    mock_recognizer = MagicMock()
    mock_result = MagicMock()

    # 2. 偽物の挙動を定義する
    # 「認識結果のテキスト」として固定の文字列を用意しておく
    mock_result.text = "これはテスト音声です"

    # Azure SDKの階層構造に合わせて偽物をセットする
    # コード内で `recognizer.recognize_once_async().get()` と呼ばれたら `mock_result` を返すように仕込む
    mock_recognizer.recognize_once_async.return_value.get.return_value = mock_result
    
    # コード内で `speech_sdk.SpeechRecognizer(...)` と呼ばれたら `mock_recognizer` を返す
    mock_speech.SpeechRecognizer.return_value = mock_recognizer

    # 3. Pythonのインポートシステムをハッキングする (ここが重要！)
    # アプリ側が `import azure.cognitiveservices.speech` をしようとしたら、
    # 本物のライブラリではなく、上で作った偽物(mock_speech)を渡すようにすり替える。
    sys.modules["azure.cognitiveservices.speech"] = mock_speech

    # --- [テスト実行: Run] ---
    yield  # ここで一旦処理が停止し、あなたの書いたテストコードが実行されます。

    # --- [後片付け: Teardown] ---
    
    # テストが終わったらここに戻ってくる。
    # すり替えたモックを削除して、元のクリーンな状態に戻す（次のテストに影響を与えないため）。
    if "azure.cognitiveservices.speech" in sys.modules:
        del sys.modules["azure.cognitiveservices.speech"]


# =================================================================
# 2. FastAPI用 HTTPクライアントの作成 (手動利用)
# =================================================================
@pytest.fixture(scope="function")
async def async_client():
    """
    FastAPIアプリにリクエストを送るための「テスト用ブラウザ」を作るフィクスチャ。
    こちらは autouse が無いので、使いたいテスト関数の引数に `async_client` と書いて呼び出す。
    """
    # テスト対象のアプリ本体と、サービスをインポート
    # (循環参照を防ぐため、関数内でインポートすることが多い)
    from src.backend.main import app
    from src.backend.services.speech import FakeSpeechService, get_speech_service

    # --- [前準備: Setup] ---

    # 1. 依存関係の上書き (Dependency Override)
    # FastAPIの強力な機能。
    # 「アプリ内で get_speech_service が必要になったら、本物ではなく FakeSpeechService を使ってね」と設定。
    # これにより、テスト中はDBや重い処理をスキップできる。
    app.dependency_overrides[get_speech_service] = lambda: FakeSpeechService()

    # 2. HTTPクライアントの作成
    # ASGITransport(app=app) : 実際のネット通信はせず、メモリ内で直接FastAPIアプリとやり取りする（高速）。
    # base_url="http://test" : テスト用の仮想URL。
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        # --- [テスト実行: Run] ---
        yield client  # 作成した client をテスト関数に渡す。

    # --- [後片付け: Teardown] ---

    # テストが終わったら、上書き設定をクリアして元に戻す。
    app.dependency_overrides.clear()


実際の使い方のイメージ
このフィクスチャファイル（例えば conftest.py という名前にします）がある状態で、テストコードは以下のように書けます。

Python


import pytest

# 引数に async_client を書くことで、上のフィクスチャが実行され、clientが渡される
@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    # 【自動】mock_azure_services が裏で勝手に走っているので、Azureへの通信はブロック済み
    # 【手動】async_client はここで受け取って使う
    
    # 1. APIを叩く
    response = await async_client.post("/api/speech-to-text", json={"audio": "..."})
    
    # 2. 結果を検証する
    assert response.status_code == 200
    assert response.json()["text"] == "これはテスト音声です" # モックで仕込んだ通りになる
