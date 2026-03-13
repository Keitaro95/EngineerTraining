"""
preprocessing/normalizer.py — テキスト正規化（2段階）
================================================
ソース: utils/text/normalizer.py:48-112
  表記ゆれを2段階で吸収する。

  [Stage 1] normalize_for_parser — パーサー用（strict）
    全角→半角 / 改行除去 / 空白統一 / カッコ統一 / カンマ変換 /
    和文スペース除去 / NFKC正規化

  [Stage 2] normalize_for_search — 検索用（緩いマッチング）
    基本正規化 + 括弧・句読点などの記号を除去
"""

import unicodedata
import re
from typing import Optional


# ---- 基本正規化（共通処理）----

def normalize_basic(text: Optional[str]) -> str:
    """全角→半角, 改行除去, 空白統一, NFKC正規化。"""
    if not text:
        return ""
    text = _to_halfwidth(text)
    text = re.sub(r"[\r\n\t]+", "", text)
    text = re.sub(r"\s", " ", text)
    text = re.sub(r" +", " ", text).strip()
    text = unicodedata.normalize("NFKC", text)
    return text


# ---- パーサー用正規化（utils/text/normalizer.py:48-88）----

def normalize_for_parser(text: Optional[str]) -> str:
    """
    パース前に適用する strict 正規化。
    基本処理 + カッコ統一・カンマ変換・和文スペース除去。
    """
    if not text:
        return ""
    text = _to_halfwidth(text)
    text = re.sub(r"[\r\n\t]+", "", text)
    text = re.sub(r"\s", " ", text)
    text = re.sub(r" +", " ", text).strip()
    # カッコ統一
    text = text.replace("（", "(").replace("）", ")")
    # カンマ → 読点
    text = text.replace(",", "、").replace("．", ".")
    # 和文の間のスペース除去
    text = _remove_japanese_spaces(text)
    text = unicodedata.normalize("NFKC", text)
    return text


# ---- 検索用正規化（utils/text/normalizer.py:91-112）----

def normalize_for_search(text: Optional[str]) -> str:
    """
    検索クエリ・対象テキストに適用する緩い正規化。
    基本正規化 + 括弧・句読点記号を除去してマッチ率を上げる。
    """
    if not text:
        return ""
    text = normalize_basic(text)
    text = re.sub(r"[()（）、。,.]", "", text)
    return text


# ---- 内部ユーティリティ ----

def _to_halfwidth(text: str) -> str:
    """全角ASCII (U+FF01-FF5E) を半角化。波ダッシュ (U+FF5E) は除外。"""
    out = []
    for ch in str(text):
        code = ord(ch)
        if code == 0x3000:              # 全角スペース
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E and code != 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)


def _remove_japanese_spaces(text: str) -> str:
    """和文文字（漢字・かな・カナ・句読点）の間のスペースのみ除去。"""
    pattern = r"(?<=[一-龯ぁ-んァ-ヶー、。])\s+(?=[一-龯ぁ-んァ-ヶー、。])"
    return re.sub(pattern, "", text)
