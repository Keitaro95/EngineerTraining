"""判定結果のレポート出力。

結論だけでなく「根拠」と「反証」を必ず並べて出す。片側だけ見せると
冷静な判断の材料にならないため。
"""

from __future__ import annotations

from .scoring import LEVELS, MessageScore, Verdict

BAR_WIDTH = 40


def _scale_bar(score: float) -> str:
    pos = int(round(score / 4.0 * (BAR_WIDTH - 1)))
    track = ["─"] * BAR_WIDTH
    track[pos] = "●"
    return "".join(track)


def _excerpt(s: MessageScore, limit: int = 46) -> str:
    text = s.message.text.replace("\n", " ")
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    reasons = "・".join(
        f"{name}{'(要確認)' if amb else ''}" for name, _, amb in s.hits
    )
    return f"  {s.message.timestamp:%m/%d %H:%M} [{s.raw:+.1f}] 「{text}」\n        └ {reasons}"


def render(verdict: Verdict) -> str:
    out: list[str] = []
    a = out.append

    a("=" * 62)
    a("  恋愛態度スコアリング結果")
    a("=" * 62)
    a("")
    a(f"  判定: 【{verdict.label}】  (スコア {verdict.score:.2f} / 4.00)")
    a(f"  {verdict.description}")
    a("")
    a(f"  拒絶 {_scale_bar(verdict.score)} 付き合いたい")
    a("       " + "  ".join(f"{lvl}" for lvl, _, _ in LEVELS).center(BAR_WIDTH))
    a("")
    a(f"  信頼度: {verdict.confidence}")
    for reason in verdict.confidence_reasons:
        a(f"    - {reason}")
    a("")

    if verdict.decisive_notes:
        a("-" * 62)
        a("  明示的な意思表示（他の指標より優先）")
        a("-" * 62)
        for note in verdict.decisive_notes:
            a(f"  ! {note}")
        a("")

    # --- 行動指標 ---------------------------------------------------------
    a("-" * 62)
    a("  行動指標（主観が入りにくい客観データ）")
    a("-" * 62)
    for m in verdict.behavior.metrics:
        if not m.usable:
            a(f"  {m.label:<22} 算出不可 — {m.detail}")
            continue
        mark = "＋" if m.score > 0.15 else ("－" if m.score < -0.15 else "±")
        a(f"  {m.label:<22} {mark} {m.score:+.2f}  ({m.detail})")
    if verdict.behavior_signal is not None:
        a("")
        a(f"  行動指標の合成: {verdict.behavior_signal:+.2f} "
          f"(算出できた指標の重み比 {verdict.behavior_coverage * 100:.0f}%)")
    a("")

    # --- 文面の根拠 -------------------------------------------------------
    signal = [s for s in verdict.message_scores if s.has_signal and s.decisive is None]
    positives = sorted([s for s in signal if s.raw > 0], key=lambda s: -s.raw)[:5]
    negatives = sorted([s for s in signal if s.raw < 0], key=lambda s: s.raw)[:5]

    a("-" * 62)
    a("  文面の根拠（好意方向）")
    a("-" * 62)
    if positives:
        for s in positives:
            a(_excerpt(s))
    else:
        a("  該当なし")
    a("")

    a("-" * 62)
    a("  文面の反証（後退・回避方向）")
    a("-" * 62)
    if negatives:
        for s in negatives:
            a(_excerpt(s))
    else:
        a("  該当なし")
    a("")

    if verdict.content_signal is not None:
        a(f"  文面の合成: {verdict.content_signal:+.2f} "
          f"（根拠を検出できたのは {len(signal)} 通 / 相手 {len(verdict.message_scores)} 通）")
    else:
        a("  文面: 根拠となる表現が3通未満のため、文面からは判定していない")
    a("")

    # --- 注意書き ---------------------------------------------------------
    a("-" * 62)
    a("  読み方の注意")
    a("-" * 62)
    a("  * これは相手の言動の統計であって、相手の内心ではない。")
    a("  * (要確認) 付きの根拠は文脈次第で誤検出する（例:「好き」は物にも使う）。")
    a("  * 信頼度が「低」のときは、判定ではなく単なるデータ不足として扱うこと。")
    a("  * 態度は変化する。期間を区切って複数回かけると推移が見える。")
    a("  * 最終的な確認手段は、この出力ではなく本人に訊くことしかない。")
    a("=" * 62)

    return "\n".join(out)
