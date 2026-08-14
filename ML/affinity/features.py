"""行動指標の抽出。

文面と違い、これらは「書き手の意図」より「実際にとった行動」を見るため、
こちらの願望が入り込みにくい。冷静な判定の主軸はこちら側に置く。
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from .lexicon import (
    INVITATION_ACCEPT,
    INVITATION_DECLINE,
    INVITATION_PATTERN,
    QUESTION_PATTERN,
)
from .schema import Message

# 会話の切れ目とみなす無応答時間（時間）
SESSION_GAP_HOURS = 6.0
# これを超えて返信がなければ「返信なし」とみなす（時間）
NO_REPLY_HOURS = 24.0


@dataclass
class Metric:
    """1 つの行動指標。value は生の値、score は [-1, 1] に正規化した評価。"""

    key: str
    label: str
    value: float | None
    score: float | None
    sample_size: int
    detail: str = ""

    @property
    def usable(self) -> bool:
        return self.score is not None


@dataclass
class Behavior:
    metrics: list[Metric] = field(default_factory=list)

    def get(self, key: str) -> Metric | None:
        return next((m for m in self.metrics if m.key == key), None)


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _turns(messages: list[Message]) -> list[list[Message]]:
    """連続する同一送信者のメッセージを 1 ターンにまとめる。"""
    turns: list[list[Message]] = []
    for m in messages:
        if turns and turns[-1][0].sender == m.sender:
            turns[-1].append(m)
        else:
            turns.append([m])
    return turns


def _reply_latencies(turns: list[list[Message]], sender: str) -> list[float]:
    """sender が相手のターンに返信するまでの秒数。会話の切れ目は除外。"""
    out = []
    for prev, cur in zip(turns, turns[1:]):
        if cur[0].sender != sender or prev[0].sender == sender:
            continue
        delta = (cur[0].timestamp - prev[-1].timestamp).total_seconds()
        if 0 <= delta <= SESSION_GAP_HOURS * 3600:
            out.append(delta)
    return out


def _latency_metric(turns: list[list[Message]]) -> Metric:
    partner = _reply_latencies(turns, "partner")
    mine = _reply_latencies(turns, "me")
    n = min(len(partner), len(mine))
    if n < 5:
        return Metric(
            "latency", "返信速度（相手 / 自分）", None, None, n,
            "サンプル不足（各5件以上必要）",
        )
    p_med = statistics.median(partner)
    m_med = statistics.median(mine)
    ratio = p_med / max(m_med, 60.0)
    # 相手が自分の 8 倍遅い → -1、8 倍速い → +1。
    # 数倍の差は日常的に起きるので、飽和は緩めに取る。
    from math import log2

    score = _clip(-log2(max(ratio, 0.01)) / 3.0)
    return Metric(
        "latency", "返信速度（相手 / 自分）", ratio, score, n,
        f"相手の中央値 {p_med / 60:.0f}分 / 自分 {m_med / 60:.0f}分",
    )


def _initiation_metric(turns: list[list[Message]]) -> Metric:
    """会話（セッション）を切り出したのがどちらか。"""
    starters: list[str] = []
    prev_end = None
    for turn in turns:
        start = turn[0].timestamp
        if prev_end is None or (start - prev_end).total_seconds() > SESSION_GAP_HOURS * 3600:
            starters.append(turn[0].sender)
        prev_end = turn[-1].timestamp
    if len(starters) < 4:
        return Metric("initiation", "相手からの会話開始率", None, None, len(starters),
                      "サンプル不足（4セッション以上必要）")
    rate = starters.count("partner") / len(starters)
    return Metric(
        "initiation", "相手からの会話開始率", rate, _clip((rate - 0.5) * 2.5), len(starters),
        f"{starters.count('partner')} / {len(starters)} セッション",
    )


def _question_metric(messages: list[Message]) -> Metric:
    """相手がこちらに質問を返す割合＝関心を向けているか。"""
    texts = [m for m in messages if m.is_partner and m.type == "text"]
    if len(texts) < 10:
        return Metric("question", "相手からの質問率", None, None, len(texts),
                      "サンプル不足（10件以上必要）")
    hits = sum(1 for m in texts if QUESTION_PATTERN.search(m.text))
    rate = hits / len(texts)
    # 質問率 20% を良好の目安とする
    return Metric(
        "question", "相手からの質問率", rate, _clip(rate / 0.20 - 1.0), len(texts),
        f"{hits} / {len(texts)} 通",
    )


def _length_metric(messages: list[Message]) -> Metric:
    p = [len(m.text) for m in messages if m.is_partner and m.type == "text" and m.text]
    q = [len(m.text) for m in messages if not m.is_partner and m.type == "text" and m.text]
    if len(p) < 10 or len(q) < 10:
        return Metric("length", "文量比（相手 / 自分）", None, None, min(len(p), len(q)),
                      "サンプル不足（各10件以上必要）")
    ratio = statistics.median(p) / max(statistics.median(q), 1)
    from math import log2

    return Metric(
        "length", "文量比（相手 / 自分）", ratio, _clip(log2(max(ratio, 0.05)) / 1.5), min(len(p), len(q)),
        f"相手 {statistics.median(p):.0f}字 / 自分 {statistics.median(q):.0f}字（中央値）",
    )


def _reaction_only_metric(turns: list[list[Message]]) -> Metric:
    """本文を返さず絵文字リアクションだけで済ませたターンの割合。"""
    partner_turns = [t for t in turns if t[0].is_partner]
    if len(partner_turns) < 10:
        return Metric("reaction_only", "リアクションのみ返信率", None, None, len(partner_turns),
                      "サンプル不足（10ターン以上必要）")
    only = sum(1 for t in partner_turns if all(m.is_reaction for m in t))
    rate = only / len(partner_turns)
    # 高いほど「省エネ対応」= マイナス。30% で -1。
    return Metric(
        "reaction_only", "リアクションのみ返信率", rate, _clip(-rate / 0.30, -1.0, 0.0),
        len(partner_turns), f"{only} / {len(partner_turns)} ターン",
    )


def _ghost_metric(turns: list[list[Message]]) -> Metric:
    """自分のターンが 24 時間放置された割合。"""
    my_turns = [(i, t) for i, t in enumerate(turns) if not t[0].is_partner]
    if len(my_turns) < 8:
        return Metric("ghost", "こちらの発言が放置された率", None, None, len(my_turns),
                      "サンプル不足（8ターン以上必要）")
    ignored = 0
    for i, turn in my_turns:
        nxt = turns[i + 1] if i + 1 < len(turns) else None
        if nxt is None:
            continue  # 末尾は保留中なので数えない
        gap = (nxt[0].timestamp - turn[-1].timestamp).total_seconds() / 3600
        if gap > NO_REPLY_HOURS:
            ignored += 1
    rate = ignored / len(my_turns)
    return Metric(
        "ghost", "こちらの発言が放置された率", rate, _clip(-rate / 0.25, -1.0, 0.0),
        len(my_turns), f"{ignored} / {len(my_turns)} ターンが24時間以上未返信",
    )


def _invitation_metric(turns: list[list[Message]]) -> Metric:
    """自分が出した誘いに対する相手の応答。最も情報量が大きい指標。"""
    results: list[str] = []
    for i, turn in enumerate(turns):
        if turn[0].is_partner:
            continue
        if not any(INVITATION_PATTERN.search(m.text) for m in turn):
            continue
        # 直後の相手ターンを応答とみなす
        reply = next((t for t in turns[i + 1:] if t[0].is_partner), None)
        if reply is None:
            results.append("no_reply")
            continue
        body = "".join(m.text for m in reply)
        if INVITATION_DECLINE.search(body):
            results.append("decline")
        elif INVITATION_ACCEPT.search(body):
            results.append("accept")
        else:
            results.append("vague")

    if len(results) < 2:
        return Metric("invitation", "誘いへの応答", None, None, len(results),
                      "検出できた誘いが2件未満")
    accept = results.count("accept")
    decline = results.count("decline") + results.count("no_reply")
    rate = accept / len(results)
    return Metric(
        "invitation", "誘いへの応答（承諾率）", rate, _clip(rate * 2.4 - 1.0), len(results),
        f"承諾 {accept} / 回避・断り {decline} / 曖昧 {results.count('vague')}",
    )


def extract(messages: list[Message]) -> Behavior:
    turns = _turns(messages)
    return Behavior(
        metrics=[
            _invitation_metric(turns),
            _initiation_metric(turns),
            _latency_metric(turns),
            _question_metric(messages),
            _ghost_metric(turns),
            _reaction_only_metric(turns),
            _length_metric(messages),
        ]
    )


# 合成時の重み。誘いへの応答と会話開始率を重く見る。
METRIC_WEIGHTS: dict[str, float] = {
    "invitation": 0.30,
    "initiation": 0.20,
    "latency": 0.15,
    "question": 0.15,
    "ghost": 0.10,
    "reaction_only": 0.05,
    "length": 0.05,
}


def composite(behavior: Behavior) -> tuple[float | None, float]:
    """行動指標の合成スコア [-1, 1] と、利用できた重みの割合を返す。"""
    total_w = 0.0
    acc = 0.0
    for m in behavior.metrics:
        if not m.usable:
            continue
        w = METRIC_WEIGHTS.get(m.key, 0.0)
        acc += w * m.score
        total_w += w
    if total_w == 0:
        return None, 0.0
    return acc / total_w, total_w / sum(METRIC_WEIGHTS.values())
