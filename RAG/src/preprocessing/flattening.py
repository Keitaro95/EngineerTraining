"""
preprocessing/flattening.py — 階層JSON → 1行1チャンク フラット化
==================================================================
ソース: parsers/pir_parser.py, parsers/to_parser.py, parsers/yss_parser.py
  - parsers/yss_parser.py   : 変更前/変更後を句点「。」で分割し 1文=1行に

概要:
  多層ネスト構造を持つ Excel / JSON を
  「1行 = 1意味単位」に分解することで、
  チャンキング・検索のノイズを最小化する。
"""

# ---- yss_parser.py: 句点分割で 1文 = 1行 ----
# parsers/yss_parser.py:88-96

def split_to_sentences(raw_text: str) -> list[str]:
    """変更前/変更後テキストを句点で分割し、空行を除去して返す。"""
    return [s.strip() for s in raw_text.split("。") if s.strip()]


# ---- rag/vector_store.py:82-126: JSON階層を再帰走査してフラット化 ----

def _flatten_json(json_data: dict, doc_id: str) -> list[dict]:
    """
    JSON階層構造（steps / sub_steps）をフラット化する。

    チャンクIDは {doc_id}:{path}:{line_index} で一意に識別。
    メタデータには階層パス・手順記号・ノード種別を保持。

    Args:
        json_data: パース済み PIR/TO JSON（"steps" キーを含む）
        doc_id   : ドキュメント識別子

    Returns:
        rows: [{"text": str, "meta": dict}, ...] のリスト
    """
    rows = []

    def walk(node: dict, path: list[str], depth: int) -> None:
        step_id   = node.get("手順記号", "")
        node_type = node.get("type", "")
        texts     = node.get("作業内容", [])

        for li, line in enumerate(texts):
            meta = {
                "id"       : f"{doc_id}:{'/'.join(path)}:{li}",
                "doc_id"   : doc_id,
                "path"     : "/".join(path),
                "line"     : li,
                "step"     : step_id,
                "type"     : node_type,
            }
            rows.append({"text": line, "meta": meta})

        for i, sub in enumerate(node.get("sub_steps", [])):
            walk(sub, path + [f"sub{i}"], depth + 1)

    for i, step in enumerate(json_data["steps"]):
        walk(step, [f"step{i}"], 0)

    return rows


# ---- to_parser.py: level_map + level_stack で正規化レベルを管理 ----
# (概念コード — 実コードは parsers/to_parser.py:206-245)

LEVEL_MAP = {
    "大項目": 1,
    "中項目": 2,
    "小項目": 3,
    "手順"  : 4,
}

def normalize_level(raw_level: str, level_stack: list) -> int:
    """
    任意深さのラベルを 1-4 の正規化レベルへ変換。
    level_stack で現在の深さを追跡する。
    """
    level = LEVEL_MAP.get(raw_level)
    if level is None:
        # 未知ラベルはスタック末尾+1とみなす
        level = (level_stack[-1] if level_stack else 0) + 1
    return level
