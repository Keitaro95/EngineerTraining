import os
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "agent-book"


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