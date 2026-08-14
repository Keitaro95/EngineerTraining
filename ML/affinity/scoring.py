"""メッセージ単位の文面スコアリングと、全体判定への集計。"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import tanh

from . import features, lexicon
from .schema import Message

LEVELS = [
    (0, "拒絶", "恋愛的な関係を明確に断られている / 関係の継続自体に消極的"),
    (1, "消極的", "やり取りは続くが、距離を取られている。恋愛的な進展の兆候は乏しい"),
    (2, "中立・友好", "友人として良好。恋愛的な好意の証拠も否定の証拠も不足している"),
    (3, "好意的", "関心を向けられている。恋愛的な可能性はあるが確定的ではない"),
    (4, "付き合いたい", "恋愛的好意がはっきり示されている"),
]

# 文面 : 行動 の配合比。行動側を重く見る。
CONTENT_WEIGHT = 0.40
BEHAVIOR_WEIGHT = 0.60


@dataclass
class MessageScore:
    message: Message
    raw: float
    hits: list[tuple[str, float, bool]] = field(default_factory=list)  # (根拠名, 重み, 曖昧か)
    decisive: str | None = None  # "accept" | "reject" | None

    @property
    def has_signal(self) -> bool:
        return bool(self.hits)


@dataclass
class Verdict:
    level: int
    label: str
    description: str
    score: float  # 0.0 - 4.0
    confidence: str
    confidence_reasons: list[str]
    content_signal: float | None
    behavior_signal: float | None
    behavior_coverage: float
    message_scores: list[MessageScore]
    behavior: features.Behavior
    decisive_notes: list[str] = field(default_factory=list)


def score_message(msg: Message) -> MessageScore:
    """相手の 1 メッセージを評価する。証拠がなければ 0（＝マイナスではない）。"""
    result = MessageScore(message=msg, raw=0.0)
    body = msg.body
    if not body:
        return result

    for rule in lexicon.DECISIVE_REJECTION:
        if rule.pattern.search(body):
            result.decisive = "reject"
            result.hits.append((rule.name, rule.weight, rule.ambiguous))
            return result

    for rule in lexicon.DECISIVE_ACCEPT:
        if rule.pattern.search(body):
            result.decisive = "accept"
            result.hits.append((rule.name, rule.weight, rule.ambiguous))
            return result

    total = 0.0
    for rule in lexicon.POSITIVE + lexicon.NEGATIVE:
        if rule.pattern.search(body):
            total += rule.weight
            result.hits.append((rule.name, rule.weight, rule.ambiguous))

    emoji_total, emojis = lexicon.emoji_score(body)
    if emojis:
        total += emoji_total
        result.hits.append((f"絵文字 {''.join(emojis)}", emoji_total, False))

    result.raw = total
    return result


def _content_signal(scores: list[MessageScore]) -> float | None:
    """証拠のあるメッセージだけを平均し、tanh で [-1, 1] に押し込める。"""
    signal = [s for s in scores if s.has_signal and s.decisive is None]
    if len(signal) < 3:
        return None
    mean = sum(s.raw for s in signal) / len(signal)
    return tanh(mean / 2.0)


def _confidence(
    n_partner: int, span_days: float, n_signal: int, coverage: float
) -> tuple[str, list[str]]:
    reasons = []
    if n_partner < 30:
        reasons.append(f"相手のメッセージが {n_partner} 通と少ない（30通以上が望ましい）")
    if span_days < 14:
        reasons.append(f"観測期間が {span_days:.0f} 日と短い（14日以上が望ましい）")
    if n_signal < 8:
        reasons.append(f"文面から根拠を検出できたのが {n_signal} 通のみ")
    if coverage < 0.6:
        reasons.append(f"行動指標のうち {coverage * 100:.0f}% しか算出できていない")

    if not reasons:
        return "高", ["データ量・観測期間ともに十分"]
    if len(reasons) >= 3:
        return "低", reasons
    return "中", reasons


def judge(messages: list[Message]) -> Verdict:
    partner_msgs = [m for m in messages if m.is_partner]
    scores = [score_message(m) for m in partner_msgs]
    behavior = features.extract(messages)
    behavior_signal, coverage = features.composite(behavior)
    content = _content_signal(scores)

    span_days = 0.0
    if len(messages) >= 2:
        span_days = (messages[-1].timestamp - messages[0].timestamp).total_seconds() / 86400
    n_signal = sum(1 for s in scores if s.has_signal)
    confidence, conf_reasons = _confidence(len(partner_msgs), span_days, n_signal, coverage)

    # --- 決定的マーカーの確認（他を上書きする） -----------------------------
    rejects = [s for s in scores if s.decisive == "reject"]
    accepts = [s for s in scores if s.decisive == "accept"]
    notes: list[str] = []
    decisive_level: int | None = None

    if rejects:
        latest = max(rejects, key=lambda s: s.message.timestamp)
        notes.append(
            f"明示的な拒絶を検出: {latest.message.timestamp:%Y-%m-%d} "
            f"「{latest.message.text[:40]}」（{latest.hits[0][0]}）"
        )
        decisive_level = 0
    if accepts:
        latest = max(accepts, key=lambda s: s.message.timestamp)
        notes.append(
            f"明示的な好意表明を検出: {latest.message.timestamp:%Y-%m-%d} "
            f"「{latest.message.text[:40]}」（{latest.hits[0][0]}）"
        )
        # 拒絶と好意の両方がある場合は、時系列で新しい方を採用する
        if not rejects or latest.message.timestamp > max(
            r.message.timestamp for r in rejects
        ):
            decisive_level = 4
        else:
            notes.append("拒絶と好意の両方を検出。より新しい発言を採用した。")

    if decisive_level is not None:
        level, label, desc = LEVELS[decisive_level]
        return Verdict(
            level=level, label=label, description=desc, score=float(decisive_level),
            confidence="高", confidence_reasons=["本人が明示的に意思表示している"],
            content_signal=content, behavior_signal=behavior_signal,
            behavior_coverage=coverage, message_scores=scores, behavior=behavior,
            decisive_notes=notes,
        )

    # --- 通常の合成 ---------------------------------------------------------
    parts: list[tuple[float, float]] = []
    if content is not None:
        parts.append((content, CONTENT_WEIGHT))
    if behavior_signal is not None:
        parts.append((behavior_signal, BEHAVIOR_WEIGHT))

    if not parts:
        return Verdict(
            level=2, label="判定不能", description="判定に足る材料がありません",
            score=2.0, confidence="低",
            confidence_reasons=["文面・行動のどちらからも指標を算出できなかった"],
            content_signal=None, behavior_signal=None, behavior_coverage=coverage,
            message_scores=scores, behavior=behavior,
        )

    combined = sum(v * w for v, w in parts) / sum(w for _, w in parts)
    score = (combined + 1.0) * 2.0  # [-1,1] -> [0,4]

    # 中央付近は「中立」に寄せる（わずかな差で断定しない）
    if score >= 3.2:
        level = 4
    elif score >= 2.5:
        level = 3
    elif score >= 1.5:
        level = 2
    elif score >= 0.8:
        level = 1
    else:
        level = 0

    _, label, desc = LEVELS[level]
    return Verdict(
        level=level, label=label, description=desc, score=score,
        confidence=confidence, confidence_reasons=conf_reasons,
        content_signal=content, behavior_signal=behavior_signal,
        behavior_coverage=coverage, message_scores=scores, behavior=behavior,
    )
