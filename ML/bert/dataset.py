"""ラベル付きデータの読み込みと、BERT 入力への変換。

入力形式（JSONL、1行1件）:
    {"text": "また今度ゆっくり話したいです", "label": 1}

label は 0 / 1 の2値。ここでは 1 = 好意シグナルあり、0 = それ以外。
別のタスク（例: 文字起こしのトラブル判定）に使う場合も形式は同じ。
"""

from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset


@dataclass
class Example:
    text: str
    label: int


def load_jsonl(path: str | Path) -> list[Example]:
    path = Path(path)
    examples: list[Example] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: JSON として読めません: {exc}") from exc

        text = str(rec.get("text", "")).strip()
        if not text:
            raise ValueError(f"{path}:{lineno}: text が空です")
        label = rec.get("label")
        if label not in (0, 1):
            raise ValueError(f"{path}:{lineno}: label は 0 か 1。実際の値: {label!r}")
        examples.append(Example(text=text, label=int(label)))

    if not examples:
        raise ValueError(f"{path}: 有効なデータが1件もありません")
    return examples


def stratified_split(
    examples: list[Example], val_ratio: float = 0.2, seed: int = 42
) -> tuple[list[Example], list[Example]]:
    """クラス比を保ったまま学習用と検証用に分ける。

    単純なシャッフル分割だと、少データのとき検証セットが片方のクラスだけに
    なってしまい、評価指標が意味をなさなくなる。
    """
    rng = random.Random(seed)
    train: list[Example] = []
    val: list[Example] = []

    for label in (0, 1):
        group = [e for e in examples if e.label == label]
        rng.shuffle(group)
        n_val = max(1, round(len(group) * val_ratio)) if len(group) > 1 else 0
        val.extend(group[:n_val])
        train.extend(group[n_val:])

    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def class_distribution(examples: list[Example]) -> dict[int, int]:
    return dict(Counter(e.label for e in examples))


class TextClassificationDataset(Dataset):
    """トークナイズは collate 側でまとめて行うため、ここでは生テキストのまま持つ。"""

    def __init__(self, examples: list[Example]):
        self.examples = examples

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Example:
        return self.examples[idx]


def make_collate_fn(tokenizer, max_length: int = 128):
    """バッチ内の最長文に合わせて動的にパディングする。

    padding="max_length" で常に固定長にすると、短文ばかりのデータでは
    無駄な計算が大量に発生する。動的パディングのほうが速く、結果は同じ。
    """

    def collate(batch: list[Example]) -> dict[str, torch.Tensor]:
        encoded = tokenizer(
            [e.text for e in batch],
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        encoded["labels"] = torch.tensor([e.label for e in batch], dtype=torch.long)
        return encoded

    return collate


def make_dataloader(
    examples: list[Example], tokenizer, batch_size: int, shuffle: bool, max_length: int = 128
) -> DataLoader:
    return DataLoader(
        TextClassificationDataset(examples),
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=make_collate_fn(tokenizer, max_length),
    )
