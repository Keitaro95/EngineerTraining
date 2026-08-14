"""日本語 BERT のファインチューニング（学習 → 評価 → 保存）。

  python -m bert.train --data data/labeled_messages.jsonl --out models/affinity-bert

Trainer ではなく素の PyTorch ループで書いている。理由は3つ:
  - 依存が減る（datasets / accelerate が不要）
  - transformers の major 更新で API が変わっても壊れにくい
  - 「ファインチューニングとは何をしているのか」がコード上に見える
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch.optim import AdamW
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bert.dataset import (  # noqa: E402
    class_distribution,
    load_jsonl,
    make_dataloader,
    stratified_split,
)

DEFAULT_MODEL = "tohoku-nlp/bert-base-japanese-v3"
LABEL_NAMES = {0: "好意シグナルなし", 1: "好意シグナルあり"}


def pick_device(requested: str | None = None) -> torch.device:
    """CUDA > MPS(Apple Silicon) > CPU の順で使えるものを選ぶ。"""
    if requested:
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@torch.no_grad()
def evaluate(model, loader, device) -> dict:
    """検証セットでの accuracy / precision / recall / F1 と混同行列を返す。"""
    model.eval()
    tp = fp = tn = fn = 0
    total_loss = 0.0
    n_batches = 0

    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        labels = batch["labels"]
        outputs = model(**batch)
        total_loss += outputs.loss.item()
        n_batches += 1
        preds = outputs.logits.argmax(dim=-1)

        tp += int(((preds == 1) & (labels == 1)).sum())
        fp += int(((preds == 1) & (labels == 0)).sum())
        tn += int(((preds == 0) & (labels == 0)).sum())
        fn += int(((preds == 0) & (labels == 1)).sum())

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "loss": total_loss / n_batches if n_batches else 0.0,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
    }


def train(args: argparse.Namespace) -> int:
    device = pick_device(args.device)
    print(f"デバイス: {device}")

    # --- 1. データ ---------------------------------------------------------
    examples = load_jsonl(args.data)
    train_ex, val_ex = stratified_split(examples, val_ratio=args.val_ratio, seed=args.seed)
    print(f"データ: 全 {len(examples)} 件 -> 学習 {len(train_ex)} / 検証 {len(val_ex)}")
    print(f"  クラス分布(全体): {class_distribution(examples)}")

    if len(examples) < 50:
        print("\n[警告] データが 50 件未満です。BERT は簡単に丸暗記するため、")
        print("       検証スコアが高くても実運用では当てになりません。")
        print("       最低でも数百件、できれば 1000 件以上を用意してください。\n")

    # --- 2. モデルとトークナイザ -------------------------------------------
    print(f"事前学習モデル: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model,
        num_labels=2,
        id2label=LABEL_NAMES,
        label2id={v: k for k, v in LABEL_NAMES.items()},
    ).to(device)

    train_loader = make_dataloader(train_ex, tokenizer, args.batch_size, shuffle=True,
                                   max_length=args.max_length)
    val_loader = make_dataloader(val_ex, tokenizer, args.batch_size, shuffle=False,
                                 max_length=args.max_length)

    # --- 3. 最適化の設定 ---------------------------------------------------
    # 事前学習済みの重みを壊さないよう、学習率は 2e-5 前後とごく小さく取る。
    # ここを 1e-3 などにすると学習済みの言語知識が飛んで性能が出ない。
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps,
    )

    # --- 4. 学習ループ -----------------------------------------------------
    best_f1 = -1.0
    out_dir = Path(args.out)

    for epoch in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        for step, batch in enumerate(train_loader, start=1):
            batch = {k: v.to(device) for k, v in batch.items()}

            outputs = model(**batch)      # 順伝播。labels を渡すと loss も返る
            loss = outputs.loss
            loss.backward()               # 逆伝播で勾配を計算

            # 勾配クリッピング: BERT は勾配が跳ねると一気に壊れるため
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            optimizer.step()              # 重みを更新
            scheduler.step()              # 学習率を減衰
            optimizer.zero_grad()         # 勾配をリセット（しないと累積する）

            running += loss.item()

        metrics = evaluate(model, val_loader, device)
        print(
            f"epoch {epoch}/{args.epochs} | "
            f"train_loss {running / len(train_loader):.4f} | "
            f"val_loss {metrics['loss']:.4f} | "
            f"acc {metrics['accuracy']:.3f} | "
            f"P {metrics['precision']:.3f} R {metrics['recall']:.3f} F1 {metrics['f1']:.3f}"
        )

        # 最良エポックのみ保存する（最終エポックが最良とは限らない）
        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            out_dir.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(out_dir)
            tokenizer.save_pretrained(out_dir)
            (out_dir / "train_info.json").write_text(
                json.dumps({
                    "base_model": args.model,
                    "epoch": epoch,
                    "metrics": metrics,
                    "n_train": len(train_ex),
                    "n_val": len(val_ex),
                    "class_distribution": class_distribution(examples),
                    "max_length": args.max_length,
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  -> 保存しました（F1 更新）: {out_dir}")

    print(f"\n学習完了。最良 F1 = {best_f1:.3f}")
    print(f"推論: python -m bert.predict {out_dir} \"テストしたい文\"")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data/labeled_messages.jsonl", help="ラベル付き JSONL")
    p.add_argument("--out", default="models/affinity-bert", help="モデルの保存先")
    p.add_argument("--model", default=DEFAULT_MODEL, help="事前学習モデル名")
    p.add_argument("--epochs", type=int, default=4)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--max-length", type=int, default=128)
    p.add_argument("--val-ratio", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default=None, help="cuda / mps / cpu（既定は自動選択）")
    args = p.parse_args(argv)

    torch.manual_seed(args.seed)
    return train(args)


if __name__ == "__main__":
    sys.exit(main())
