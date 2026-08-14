"""学習済みモデルを対話的に試す。

  .venv/bin/python -m bert.interactive

モデルの読み込みは起動時の1回だけ。あとは文を入力するたびに即座に判定する。
終了は Ctrl-D か "exit"。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bert.predict import AffinityClassifier  # noqa: E402


def bar(p: float, width: int = 24) -> str:
    filled = int(p * width)
    return "█" * filled + "░" * (width - filled)


def verdict(p: float) -> str:
    """確率をそのまま断定に使わない。中間帯は「判断保留」として明示する。"""
    if p >= 0.70:
        return "好意シグナルあり"
    if p >= 0.55:
        return "やや好意寄り（弱い）"
    if p > 0.45:
        return "判断できない（中間）"
    if p > 0.30:
        return "やや非好意寄り（弱い）"
    return "好意シグナルなし"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                               formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="models/affinity-bert", help="モデルのディレクトリ")
    p.add_argument("--device", default=None)
    args = p.parse_args(argv)

    print("モデルを読み込んでいます...")
    clf = AffinityClassifier(args.model, device=args.device)
    print(f"準備完了（device={clf.device}）\n")
    print("判定したい文を入力してください。終了は Ctrl-D または exit\n")

    history: list[float] = []
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line in ("exit", "quit", ":q"):
            break

        result = clf.predict([line])[0]
        prob = result["p_positive"]
        history.append(prob)

        print(f"  {bar(prob)}  P(好意)={prob:.3f}  -> {verdict(prob)}")
        if 0.45 < prob < 0.55:
            print("  ※ 0.5 付近はモデルが判断できていないという意味。根拠にはできない。")
        print()

    if history:
        mean = sum(history) / len(history)
        print(f"\n入力 {len(history)} 件の平均 P(好意) = {mean:.3f}"
              f"（文面スコア {mean * 2 - 1:+.3f}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
