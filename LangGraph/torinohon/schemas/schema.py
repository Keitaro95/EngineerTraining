import operator
from typing import Annotated
from pydantic import BaseModel, Field

class State(BaseModel):
    query: str = Field(..., description="ユーザーからの質問")
    current_role: str = Field(default="", description="回答ロール")
    """
    Annotatedは型ヒントをつけると同時に
    型の付け方のルールを与えられる

    LangGraph の場合 — 更新ルールとして使う：
    `operator.add` はリストに対しては「結合」を意味します。
    node_a 実行後 → messages: ["こんにちは"]
    node_b 実行後 → messages: ["こんにちは", "元気ですか？"]  ← 追記される！
    """
    messages: Annotated[list[str], operator.add] = Field(default=[], description="回答履歴")
    current_judge: bool = Field(default=False, description="品質チェックの結果")
    current_reason: str = Field(default="", description="品質チェックの判定理由")