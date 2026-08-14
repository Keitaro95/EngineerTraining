"""学習済みモデルを読み込んで推論する。

  python -m bert.predict models/affinity-bert "また今度ゆっくり話したいです"
  python -m bert.predict models/affinity-bert --file data/new_messages.txt
  python -m bert.predict models/affinity-bert --file msgs.txt --json

学習時と同じ前処理（同じ tokenizer）を使う必要があるため、tokenizer も
モデルと同じディレクトリから読む。ここを別物にすると静かに精度が落ちる。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bert.train import pick_device  # noqa: E402


class AffinityClassifier:
    """保存済みモデルをラップして、テキスト -> 確率 を返すだけの薄い層。"""

    def __init__(self, model_dir: str | Path, device: str | None = None, max_length: int = 128):
        model_dir = Path(model_dir)
        if not model_dir.exists():
            raise FileNotFoundError(
                f"モデルが見つかりません: {model_dir}\n"
                "先に python -m bert.train を実行してください。"
            )
        self.device = pick_device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.model.eval()  # dropout を切る。忘れると推論結果が毎回ぶれる
        self.max_length = max_length
        self.id2label = self.model.config.id2label

    @torch.no_grad()
    def predict(self, texts: list[str], batch_size: int = 32) -> list[dict]:
        results: list[dict] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            inputs = self.tokenizer(
                chunk, padding=True, truncation=True,
                max_length=self.max_length, return_tensors="pt",
            ).to(self.device)

            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu()

            for text, prob in zip(chunk, probs):
                label_id = int(prob.argmax())
                results.append({
                    "text": text,
                    "label": label_id,
                    "label_name": self.id2label.get(label_id, str(label_id)),
                    "p_positive": float(prob[1]),
                    "confidence": float(prob[label_id]),
                })
        return results

    def affinity_score(self, texts: list[str]) -> float:
        """[-1, 1] に変換した文面スコア。既存の集計にそのまま差し込める。

        affinity/scoring.py の content_signal と同じ値域にしてあるので、
        ルールベースの文面スコアの代わりに使える。
        """
        if not texts:
            return 0.0
        preds = self.predict(texts)
        return sum(p["p_positive"] for p in preds) / len(preds) * 2.0 - 1.0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model_dir", help="学習済みモデルのディレクトリ")
    p.add_argument("texts", nargs="*", help="判定したい文（複数可）")
    p.add_argument("--file", help="1行1文のテキストファイル")
    p.add_argument("--json", action="store_true", help="JSON で出力")
    p.add_argument("--device", default=None)
    args = p.parse_args(argv)

    texts = list(args.texts)
    if args.file:
        texts.extend(
            line.strip() for line in Path(args.file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if not texts:
        print("エラー: 判定する文を指定してください（引数か --file）", file=sys.stderr)
        return 1

    clf = AffinityClassifier(args.model_dir, device=args.device)
    results = clf.predict(texts)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            bar_len = int(r["p_positive"] * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"{bar} P(好意)={r['p_positive']:.3f}  「{r['text']}」")
        if len(results) > 1:
            print(f"\n文面スコア（[-1,1] 換算）: {clf.affinity_score(texts):+.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
