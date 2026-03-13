"""
rag/rescue_fallback.py — レスキュー処理（LLMフォールバック）
=============================================================
ソース: core/workflow.py:502-514
概要:
  RAG ベクトル検索の閾値（0.80）未達だった結果に対し、
  フル LLM プロセッサで再処理するフォールバック機構。

  フロー:
    RAG 検索 → below_threshold フラグ付きで返却
    → rescue_below_threshold() で全差分を LLM に投げ直す
    → rescue_json があれば context.rescue_results に追記

  使用条件:
    config.use_full_llm_mode = True かつ full_llm_processor が設定済み
"""


def run_rescue_if_needed(
    config,
    full_llm_processor,
    job_name: str,
    old_to_blocks: list,
    new_to_blocks: list,
    original_results: list,
    original_job_json: dict,
    rescue_results: list,
) -> None:
    """
    RAG 閾値未達の結果に対し LLM フォールバックを実行。
    core/workflow.py:502-514 の処理をスタンドアロン化。

    Args:
        config             : use_full_llm_mode フラグを持つ設定オブジェクト
        full_llm_processor : rescue_below_threshold() を持つ LLM プロセッサ
        job_name           : 処理対象の手順書名
        old_to_blocks      : 旧TO ブロックリスト
        new_to_blocks      : 新TO ブロックリスト
        original_results   : RAG 検索の結果リスト（below_threshold 含む）
        original_job_json  : 元手順書 JSON
        rescue_results     : rescue 結果を追記するリスト（in-place）
    """
    if not (config.use_full_llm_mode and full_llm_processor):
        return

    rescue_json = full_llm_processor.rescue_below_threshold(
        job_name=job_name,
        old_to_blocks=old_to_blocks,
        new_to_blocks=new_to_blocks,
        original_results=original_results,
        original_job_json=original_job_json,
    )

    if rescue_json:
        rescue_results.append((rescue_json, job_name, original_job_json))


# ---- rescue_below_threshold の役割（概念） ----
#
# 1. original_results の中から below_threshold=True のものを抽出
# 2. 旧TO / 新TO / 差分 / 元手順書 を FullLLMUpdatePrompt に渡す
# 3. LLM の出力を parse して rescue_json を返す
#
# これにより、RAG が意味的に見つけられなかった箇所を
# LLM の文脈理解で補完する「二段構え」の精度向上を実現する。
