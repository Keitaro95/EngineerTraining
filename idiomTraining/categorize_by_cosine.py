"""
categorize_by_cosine.py

before文リストとafter文リストのペアを受け取り、
コサイン類似度に基づいて changed / removed / added に分類する。

アルゴリズム（greedy bipartite matching）:

  [Step 1] 全組み合わせのコサイン類似度を計算
    before_list × after_list の全ペア (b_idx, a_idx, sim) を列挙する。

  [Step 2] sim の高い順に並べる
    最も類似度が高いペアから優先的に処理する。

  [Step 3] greedy マッチング
    上から順にペアを見て、両インデックスがまだ未使用なら判定する:
    - sim == 1.0       → no_change（記録せず、両インデックスを使用済みにする）
    - sim >= threshold → changed（記録し、両インデックスを使用済みにする）
    - sim < threshold  → スキップ（continue）

  [Step 4] 残ったインデックスを分類
    - 未使用の before インデックス → removed（削除された文）
    - 未使用の after  インデックス → added（追加された文）
"""

import settings as settings_module


def categorize_by_cosine(
    before_list: list[str],
    after_list: list[str],
    threshold: float = 0.7,
) -> dict:
    """
    before文リストとafter文リストを突き合わせ、
    コサイン類似度と閾値に基づいて分類する。
    settings.calc（lifespan で初期化済みシングルトン）を使用。

    Args:
        before_list: 変更前の文リスト
        after_list:  変更後の文リスト
        threshold:   changed / removed+added の境界閾値（デフォルト 0.7）

    Returns:
        {
            "changed": [{"old": "...", "new": "..."}, ...],
            "removed": [{"old": "...", "new": ""}, ...],
            "added":   [{"old": "",    "new": "..."}, ...],
        }
    """
    calc = settings_module.calc
    assert calc is not None, "settings.calc が初期化されていません（lifespan を確認してください）"
    result = {"changed": [], "removed": [], "added": []}

    # Step 1: 全組み合わせのコサイン類似度を計算
    all_pairs = []
    for b_idx in range(len(before_list)):
        for a_idx in range(len(after_list)):
            sim = round(calc.analyse_single(before_list[b_idx], after_list[a_idx]), 4)
            all_pairs.append((b_idx, a_idx, sim))

    # Step 2: sim の高い順に並べる
    all_pairs.sort(key=lambda x: x[2], reverse=True)

    # Step 3: greedy マッチング
    used_b = set()
    used_a = set()

    for b_idx, a_idx, sim in all_pairs:
        # どちらか一方でも使用済みならスキップ
        if b_idx in used_b or a_idx in used_a:
            continue

        if sim == 1.0:
            # 完全一致 → no_change（結果に記録せず、インデックスを消費）
            used_b.add(b_idx)
            used_a.add(a_idx)
        elif sim >= threshold:
            # 高類似度 → changed
            result["changed"].append({"old": before_list[b_idx], "new": after_list[a_idx]})
            used_b.add(b_idx)
            used_a.add(a_idx)
        else:
            # sim < threshold → マッチしない。スキップして次のペアへ
            continue

    # Step 4: 残ったインデックスを removed / added に分類
    for b_idx in range(len(before_list)):
        if b_idx not in used_b:
            result["removed"].append({"old": before_list[b_idx], "new": ""})

    for a_idx in range(len(after_list)):
        if a_idx not in used_a:
            result["added"].append({"old": "", "new": after_list[a_idx]})

    return result
