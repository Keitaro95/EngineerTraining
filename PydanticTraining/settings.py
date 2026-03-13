import os
from pydantic_settings import BaseSettings, SettingsConfigDict

"""
BaseSettings は BaseModel を継承していて、
.env ファイルや os.environ から値を取得して、
型チェック付きの設定オブジェクトを作るクラス。

Python はまずこのクラスを読み込んだ瞬間に
「クラスオブジェクト」を作る。この辞書（__dict__）がクラスのメモリ領域。
ここに メソッド・クラス変数・型アノテーション が格納される。
Settings.__dict__.keys()
# → ['__module__', 'model_config', 'OPENAI_API_KEY', ..., '_set_env_variables', '__init__']

② インスタンス生成時
settings = Settings()

が呼ばれると、裏で2段階のメモリ操作が起きる：
a. __new__ （BaseModel側で定義）
→ 空のインスタンスをヒープ上に確保
→ settings.__dict__ = {} がまだ空

b. __init__（あなたの定義）
ここで初めて値が詰め込まれる。
だから def __init__でenv読み込みが必要


"""
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
         # .envからファイルを読み出す
        env_file = ".env",
        env_file_encoding = "utf-8",
    )
    """
    このように設定値を型アノテーションつきで定義することができる
    """
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "agent-book"

    openai_embedding_model: str = "text-embedding-3-small"

    def __init__(self, **values):
        # 親クラスBaseSettingsのinitを呼ぶ
        # こうして .envファイルが読み込まれる
        super().__init__(**values)
        # 下に定義したメソッドを呼ぶ
        self._set_env_variables()

    def _set_env_variables(self):
        #全てのフィールドをループ処理で読み込む
        for key in self.__annotations__.keys():

            # 大文字は環境変数にしましょう
            # temperature のようなアプリケーション内部の設定値と区別しましょう
            if key.isupper():
                os.environ[key] = getattr(self, key)

