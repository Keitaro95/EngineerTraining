from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from datetime import date

class User(BaseModel):
    name: str = Field(..., min_length=4, max_length=16)
    age: int = Field(..., ge=18, le=99)
    birthday: date
    token: str = Field(..., min_length=1) # このフィールドは必須（Required）である


    @field_validator("name")
    @classmethod
    def validate_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("name must be alphanumeric")
        return v
    
    # model全体を検証する。複数のフィールドの値を組み合わせてチェックしたい場合
    # after:すべてのフィールドの型チェックと、個別のフィールドバリデーション（@field_validator）が完了し、モデルのインスタンスが作成された直後
    @model_validator(mode="after")
    def validate_age_match(self) -> "User":
        today = date.today()
        birthday = date(self.birthday.year, self.birthday.month, self.birthday.day)
        # 「今日の日付」が「今年の誕生日」より前（つまり誕生日がまだ来ていない）なら True=1、誕生日を過ぎていれば False=0
        age = today.year - birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        if not self.age == age:
            raise ValueError("your age doesn't match your birthdate")
        return self

if __name__ == "__main__":
    try:
        user = User(name="alpha", age=25, birthday=date(2000, 9, 9), token="")
        print("your user instance is validated")
    except ValidationError as e:
        print(e)