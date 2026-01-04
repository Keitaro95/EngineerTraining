from typing import Self
from pydantic import BaseModel, ValidationError, model_validator

class User(BaseModel):
    name: str
    password1: str
    password2: str
    token: str

    # mode="before" 
    # 「入力データ（辞書）の段階でしかできないもの」や「フィールドの型変換や個別バリデーションの前に検証したいもの」です。
    # 返すのは「辞書（dict）」です。フィールドの型や値そのものの詳細なチェックは@field_validator や mode="after" で行うのが一般的です。
    @model_validator(mode="before")
    @classmethod
    def check_input_dict(cls, data: dict) -> dict:
        if "token" in data and not any(char.isdigit() for char in data["token"]):
            raise ValueError("token has to be include number")
        if "age" in data and isinstance(data["age"], str):
            data["age"] = int(data["age"])    
        return data
    

if __name__ == "__main__":
    try:
        User(name="Rei", password1="123", password2="123", token="aiueo")
    except ValidationError as e:
        print(e)

    try:
        # ageがstrでもintに補正される
        user = User(name="Rei", password1="123", password2="123", token="t1")
        print("your second data is validatad")
    except ValidationError as e:
        print(e)