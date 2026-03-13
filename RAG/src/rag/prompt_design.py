"""
rag/prompt_design.py — プロンプト設計 & コンテキスト組立
=========================================================
ソース: llm/prompts/keyword_prompt.py, llm/prompts/full_llm_update_prompt.py, diff/analyzer.py:113-269
  - llm/prompts/full_llm_update_prompt.py
  - diff/analyzer.py:113-269

概要:
  A) キーワード抽出プロンプト
     部品名・整備作業名・部品Noを確信度付きJSONで抽出。
     部品No判定規則（長さ6-15文字、英数字+ハイフンのみ等）を明示指定。

  B) 完全LLM更新プロンプト
     旧TO / 新TO / 差分 / 元JOBマニュアルの4点セットをコンテキストとして渡す。
     出力形式（手順書JSONのステップ全体）を厳密に指定。

  C) コンテキスト組立（diff/analyzer.py）
     追加文 → 前後文脈をRAGで取得してLLMに渡す
     変更文 → 対応する元文をRAGで取得してLLMに渡す
"""

import json
from typing import Any


# ======================================================================
# A) キーワード抽出プロンプト
#    llm/prompts/keyword_prompt.py:25-79
# ======================================================================

KEYWORD_SYSTEM_PROMPT = "あなたは日本語の機械構造と整備に詳しい専門エンジニアです。"

def build_keyword_prompt(texts: str) -> str:
    """
    整備手順テキストから部品名・整備作業名・部品Noを確信度付きJSONで抽出するプロンプト。

    部品No 判定規則（精度最優先）:
      - 英字を1文字以上含む
      - 全体の長さが 6〜15 文字
      - 英数字およびハイフン（-）のみ
      - 単位（in-lb, kg-m 等）は除外
      - スラッシュ含む場合はスラッシュ前まで（例: M65258/1-842 → M65258）
    """
    return f"""
あなたは日本語の航空機整備および構造部品の専門家です。
以下の整備手順テキストから「部品名」「整備作業名」「部品No」を抽出し、
整備作業としての妥当性に基づき確信度（0.0〜1.0）を付与してください。

=== 抽出仕様 ===

■1. 抽出対象
「部品名」＋「整備動作（取付・取外・交換・点検・締付・調整 など）」＋「部品No（該当時）」

■2. 部品No 判定規則（精度最優先）
以下すべてを満たすもののみ部品Noとみなす：
- 英字を1文字以上含む
- 全体の長さが 6〜15 文字
- 英数字およびハイフン（-）のみ
- 通常の単位（in-lb、kg-m、mm、psi 等）は除外
- 文脈的に部品名称の直後、または P/N・部品番号 の後に続くものは優先
- スラッシュを含む場合はスラッシュ前までを部品Noとする（例：M65258/1-842 → M65258）

■3. 整備動作語
- 明確な作業語：取付ける、取り外す、交換する、締付ける、点検する、検査する、調整する
- 「〜すること」「〜なければならない」「〜こと」などの命令形も含める

■4. 除外ルール
- 抽象語（判断、影響、確認、調査など）は除外
- 入力に存在しない語は生成しない

■5. 出力ルール
- 文中に部品Noがない場合、部品Noは []
- 1文に複数の部品Noが連続する場合は配列にまとめる
- JSONのみ出力し、説明文は不要

=== 出力形式 ===
[
{{"部品名": "...", "整備作業名": "...", "部品No": ["..."], "確信度": 0.00}},
]

=== 入力 ===
{texts}
"""


# ======================================================================
# B) 完全LLM更新プロンプト
#    llm/prompts/full_llm_update_prompt.py:153-200
# ======================================================================

def build_full_llm_update_prompt(
    old_to: dict[str, Any],
    new_to: dict[str, Any],
    diff_info: list[dict[str, Any]],
    original_job: dict[str, Any],
) -> str:
    """
    旧TO / 新TO / 差分 / 元JOBマニュアルの4点セットを渡す更新プロンプト。

    LLMへの指示（system_prompt）は FullLLMUpdatePrompt.SYSTEM_PROMPT を参照:
      - 差分を「注意書き」「実作業工程」に分類
      - 類似文があれば置換、なければ sub_steps に追加
      - JSON以外の出力を禁止
    """
    return f"""以下の入力データに基づいて、手順書を更新してください。

【入力データ】

1. 旧TO手順書:
```json
{json.dumps(old_to, ensure_ascii=False, indent=2)}
```

2. 新TO手順書:
```json
{json.dumps(new_to, ensure_ascii=False, indent=2)}
```

3. 差分情報:
```json
{json.dumps(diff_info, ensure_ascii=False, indent=2)}
```

4. 元手順書（更新対象）:
```json
{json.dumps(original_job, ensure_ascii=False, indent=2)}
```

【出力】
上記のルールに従って更新した手順書のJSONを出力してください。
JSON以外の説明は不要です。JSONのみを出力してください。
"""


# ======================================================================
# C) コンテキスト組立（diff/analyzer.py:113-269）
# ======================================================================

def build_context_for_added(
    new_sentence: str,
    prev_context: str,
    next_context: str,
    rag_retrieve_fn,
) -> dict:
    """
    追加文の処理: 前後文脈を RAG で検索してコンテキストを組立。
    diff/analyzer.py:113-188 に対応。

    Returns:
        {"new_sentence", "prev_hit", "next_hit", "prev_context", "next_context"}
    """
    prev_hit = rag_retrieve_fn(prev_context) if prev_context else None
    next_hit = rag_retrieve_fn(next_context) if next_context else None

    # 閾値未満ヒットは除外
    prev_hit = None if (prev_hit and prev_hit.get("below_threshold")) else prev_hit
    next_hit = None if (next_hit and next_hit.get("below_threshold")) else next_hit

    return {
        "new_sentence" : new_sentence,
        "prev_context" : prev_context,
        "next_context" : next_context,
        "prev_hit"     : prev_hit,
        "next_hit"     : next_hit,
    }


def build_context_for_changed(
    old_sentence: str,
    new_sentence: str,
    pair_words: list,
    rag_retrieve_fn,
    llm_generate_fn,
) -> dict:
    """
    変更文の処理: 旧文で RAG 検索 → 対応する元文を LLM に渡す。
    diff/analyzer.py:192-269 に対応。

    Returns:
        {"old_sentence", "new_sentence", "hit", "after_text"}
    """
    hit = rag_retrieve_fn(old_sentence, pair_words)
    is_below = hit.get("below_threshold", False) if hit else False

    after_text = llm_generate_fn(
        old_to=old_sentence,
        new_to=new_sentence,
        old_job=hit["text"] if hit else "",
    ) if hit else ""

    return {
        "old_sentence": old_sentence,
        "new_sentence": new_sentence,
        "hit"         : None if is_below else hit,
        "after_text"  : after_text,
    }
