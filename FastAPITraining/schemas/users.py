from pydantic import BaseModel, ConfigDict

"""
UserForbid(name="John", age=20)
未知のクエリパラメーターがある
インジェクション攻撃じゃん！→422エラー返すよ

FastAPIでクエリパラメータモデルに"forbid"を設定すると
未知のクエリパラメータを拒否できる。
クエリパラメーターからのインジェクション攻撃を拒絶できる。
GET /items/?limit=10&unknown=xに対して422エラーを返すことで、APIの厳密性を保てる。

allow
ignore
forbid
"""
class UserForbid(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str

"""
クエリパラメータの型だよ
"""
class FilterParams(BaseModel):
    model_config = {"extra": }