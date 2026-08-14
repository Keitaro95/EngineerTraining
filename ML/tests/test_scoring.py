"""python3 -m unittest discover tests で実行。"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from affinity import load_messages, score_message  # noqa: E402
from affinity.features import extract  # noqa: E402
from affinity.schema import Message, SchemaError  # noqa: E402
from affinity.scoring import judge  # noqa: E402

BASE = datetime(2026, 6, 1, 12, 0)


def msg(minutes: int, sender: str, text: str, mtype: str = "text") -> Message:
    return Message(
        index=0, timestamp=BASE + timedelta(minutes=minutes),
        sender=sender, type=mtype, text=text,
    )


def conversation(rows: list[tuple[int, str, str]]) -> list[Message]:
    out = [msg(m, s, t) for m, s, t in rows]
    for i, m in enumerate(out):
        m.index = i
    return out


class TestMessageScore(unittest.TestCase):
    def test_明示的な拒絶は決定的マーカーになる(self):
        s = score_message(msg(0, "partner", "ごめんなさい、友達としてしか見られないです"))
        self.assertEqual(s.decisive, "reject")

    def test_交際の同意は決定的マーカーになる(self):
        s = score_message(msg(0, "partner", "私でよければ付き合いたいです"))
        self.assertEqual(s.decisive, "accept")

    def test_誘いの表現は加点される(self):
        s = score_message(msg(0, "partner", "今度二人でご飯行きましょう！"))
        self.assertGreater(s.raw, 2.0)

    def test_回避表現は減点される(self):
        s = score_message(msg(0, "partner", "ごめん、忙しくて行けないです"))
        self.assertLess(s.raw, -1.0)

    def test_また今度に願望が続く場合は回避扱いしない(self):
        avoid = score_message(msg(0, "partner", "また今度で"))
        want = score_message(msg(0, "partner", "また今度ゆっくり話したいです"))
        self.assertLess(avoid.raw, 0)
        self.assertGreater(want.raw, avoid.raw)

    def test_根拠がない文は0点でマイナスにはならない(self):
        s = score_message(msg(0, "partner", "明日は雨らしいですね"))
        self.assertEqual(s.raw, 0.0)
        self.assertFalse(s.has_signal)

    def test_恋愛温度の高い絵文字は加点される(self):
        cold = score_message(msg(0, "partner", "ありがとう👍"))
        hot = score_message(msg(0, "partner", "ありがとう❤️"))
        self.assertGreater(hot.raw, cold.raw)

    def test_同じ絵文字の連打は頭打ちになる(self):
        two = score_message(msg(0, "partner", "❤️❤️"))
        many = score_message(msg(0, "partner", "❤️❤️❤️❤️❤️❤️"))
        self.assertEqual(two.raw, many.raw)


class TestBehavior(unittest.TestCase):
    def test_誘いを断られると承諾率が下がる(self):
        conv = conversation([
            (0, "me", "今度ご飯行きませんか"),
            (10, "partner", "ごめんなさい、忙しくて"),
            (2000, "me", "映画でもどうですか"),
            (2010, "partner", "すみません、予定があって"),
            (4000, "me", "空いてる日ありますか"),
            (4010, "partner", "しばらく厳しいです"),
        ])
        m = extract(conv).get("invitation")
        self.assertIsNotNone(m.score)
        self.assertLess(m.score, 0)

    def test_誘いに応じると承諾率が上がる(self):
        conv = conversation([
            (0, "me", "今度ご飯行きませんか"),
            (10, "partner", "いいですね！行きたいです"),
            (2000, "me", "映画でもどうですか"),
            (2010, "partner", "ぜひ！楽しみ"),
            (4000, "me", "土曜空いてますか"),
            (4010, "partner", "大丈夫です"),
        ])
        m = extract(conv).get("invitation")
        self.assertGreater(m.score, 0)

    def test_サンプル不足の指標は算出不可になる(self):
        conv = conversation([(0, "me", "やあ"), (5, "partner", "どうも")])
        for metric in extract(conv).metrics:
            self.assertFalse(metric.usable, metric.key)


class TestJudge(unittest.TestCase):
    def test_材料がなければ判定不能になる(self):
        v = judge(conversation([(0, "me", "やあ"), (5, "partner", "どうも")]))
        self.assertEqual(v.label, "判定不能")
        self.assertEqual(v.confidence, "低")

    def test_拒絶の明言は他の指標を上書きする(self):
        rows = [(i * 60, "partner" if i % 2 else "me", "楽しかった！また会いたいです😊")
                for i in range(40)]
        rows.append((3000, "partner", "ごめんなさい、恋愛対象としては見られないです"))
        v = judge(conversation(rows))
        self.assertEqual(v.level, 0)
        self.assertEqual(v.label, "拒絶")
        self.assertTrue(v.decisive_notes)

    def test_拒絶より新しい好意表明が優先される(self):
        rows = [
            (0, "partner", "友達としてしか見られないです"),
            (100000, "partner", "やっぱり付き合いたいです"),
        ]
        v = judge(conversation(rows))
        self.assertEqual(v.level, 4)

    def test_信頼度はデータ量が少ないと下がる(self):
        conv = conversation([
            (0, "me", "やあ"),
            (5, "partner", "楽しかったです😊"),
            (10, "partner", "また会いたいですね"),
            (15, "partner", "今度二人で行きましょう"),
        ])
        self.assertIn(judge(conv).confidence, ("低", "中"))


class TestSchema(unittest.TestCase):
    def test_JSONLを読み込んで時系列に並べ替える(self):
        rows = [
            {"timestamp": "2026-06-02T10:00:00", "sender": "partner", "text": "後"},
            {"timestamp": "2026-06-01T10:00:00", "sender": "me", "text": "先"},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
            path = f.name
        messages = load_messages(path)
        self.assertEqual([m.text for m in messages], ["先", "後"])
        self.assertEqual([m.index for m in messages], [0, 1])

    def test_不正なsenderは弾かれる(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": "2026-06-01T10:00:00", "sender": "him"}))
            path = f.name
        with self.assertRaises(SchemaError):
            load_messages(path)

    def test_リアクションの参照先が並べ替え後も保たれる(self):
        rows = [
            {"timestamp": "2026-06-02T10:00:00", "sender": "partner",
             "type": "reaction", "text": "❤️", "reaction_to": 1},
            {"timestamp": "2026-06-01T10:00:00", "sender": "me", "text": "対象"},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
            path = f.name
        messages = load_messages(path)
        reaction = next(m for m in messages if m.is_reaction)
        self.assertEqual(messages[reaction.reaction_to].text, "対象")


if __name__ == "__main__":
    unittest.main()
