"""入力データのスキーマ定義とローダ。

想定する入力は JSONL（1行1メッセージ）または JSON 配列。
リアクション（絵文字だけの反応）も 1 メッセージとして表現する。

  {"timestamp": "2026-08-01T21:03:00", "sender": "partner", "type": "text",
   "text": "今日は楽しかった！また行こうね"}
  {"timestamp": "2026-08-01T21:05:00", "sender": "partner", "type": "reaction",
   "text": "❤️", "reaction_to": 12}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SENDERS = ("me", "partner")
MSG_TYPES = ("text", "reaction", "sticker", "image", "call")


@dataclass
class Message:
    index: int
    timestamp: datetime
    sender: str  # "me" | "partner"
    type: str  # "text" | "reaction" | "sticker" | "image" | "call"
    text: str = ""
    reaction_to: int | None = None

    @property
    def is_partner(self) -> bool:
        return self.sender == "partner"

    @property
    def is_reaction(self) -> bool:
        return self.type == "reaction"

    @property
    def body(self) -> str:
        """本文。スタンプ・画像・通話は本文なし扱い。"""
        return self.text if self.type in ("text", "reaction") else ""


class SchemaError(ValueError):
    pass


def _parse_timestamp(raw: object, where: str) -> datetime:
    if isinstance(raw, datetime):
        return raw
    if not isinstance(raw, str):
        raise SchemaError(f"{where}: timestamp が文字列ではありません: {raw!r}")
    text = raw.strip().replace("/", "-").replace(" ", "T")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise SchemaError(
            f"{where}: timestamp を解釈できません: {raw!r} "
            "(ISO8601 形式、例 2026-08-01T21:03:00 を想定)"
        ) from exc


def _build(record: dict, index: int, where: str) -> Message:
    sender = record.get("sender")
    if sender not in SENDERS:
        raise SchemaError(f"{where}: sender は {SENDERS} のいずれか。実際の値: {sender!r}")

    msg_type = record.get("type", "text")
    if msg_type not in MSG_TYPES:
        raise SchemaError(f"{where}: type は {MSG_TYPES} のいずれか。実際の値: {msg_type!r}")

    reaction_to = record.get("reaction_to")
    if reaction_to is not None and not isinstance(reaction_to, int):
        raise SchemaError(f"{where}: reaction_to は整数（対象メッセージの index）")

    return Message(
        index=index,
        timestamp=_parse_timestamp(record.get("timestamp"), where),
        sender=sender,
        type=msg_type,
        text=str(record.get("text", "") or ""),
        reaction_to=reaction_to,
    )


def load_messages(path: str | Path) -> list[Message]:
    """JSONL / JSON 配列を読み込み、時系列順の Message リストを返す。"""
    path = Path(path)
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise SchemaError(f"{path}: ファイルが空です")

    records: list[dict]
    if raw.lstrip().startswith("["):
        records = json.loads(raw)
    else:
        records = []
        for lineno, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SchemaError(f"{path}:{lineno}: JSON として読めません: {exc}") from exc

    messages = [_build(rec, i, f"{path} [{i}]") for i, rec in enumerate(records)]
    messages.sort(key=lambda m: m.timestamp)
    # ソート後に index を振り直す（reaction_to は元 index を指すため対応表を作る）
    remap = {m.index: i for i, m in enumerate(messages)}
    for new_index, m in enumerate(messages):
        if m.reaction_to is not None:
            m.reaction_to = remap.get(m.reaction_to)
        m.index = new_index
    return messages
