"""メッセージ履歴から相手の恋愛態度をルールベースでスコアリングする。"""

from .report import render
from .schema import Message, SchemaError, load_messages
from .scoring import Verdict, judge, score_message

__all__ = [
    "Message",
    "SchemaError",
    "Verdict",
    "judge",
    "load_messages",
    "render",
    "score_message",
]
