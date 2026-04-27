"""
mcp_server_google_sheets.py – FastMCP × Google Sheets MCP サーバー

このスクリプトは、FastMCP を利用して以下のワークフローを実現する MCP サーバーです。

1. 任意形式（PDF/DOCX/XLSX/TXT）のドキュメントを LLM クライアントから送信
2. `parse_document` ツールでテキスト／表データを抽出し、構造化 JSON（職歴・スキル）を生成
3. `update_google_sheet` ツールで構造化 JSON を受け取り、指定スプレッドシートに書き込み

---
実行方法:
    $ python mcp_server_google_sheets.py
    # STDIO 経由で MCP プロトコルに応答します。

LLM からの呼び出し例:
    1) ツール parse_document に file_bytes, filename を渡す → JSON
    2) その JSON と spreadsheet_id を update_google_sheet に渡す → "Google Sheets を更新しました。"
"""
import os
import io
import magic
import pandas as pd
from typing import Dict, Any, List

from fastmcp import FastMCP
from pdfminer.high_level import extract_text
from docx import Document as DocxDocument
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------
# MCP サーバーの初期化
# ------------------------------
mcp = FastMCP(name="DocToGoogleSheets")

# ------------------------------
# Google Sheets クライアントの初期化関数
# ------------------------------
def init_gs_client() -> gspread.Client:
    """
    サービスアカウント JSON キーを用いて gspread クライアントを初期化する。
    環境変数 GOOGLE_APPLICATION_CREDENTIALS にキーのパスを設定しておくこと。
    """
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""), scope
    )
    return gspread.authorize(creds)

# グローバルにクライアントを生成しておく
GS_CLIENT = init_gs_client()

# ------------------------------
# ドキュメント解析ツール
# ------------------------------
@mcp.tool
def parse_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    LLM から渡されたファイルのバイト列とファイル名を受け取り、
    拡張子／MIME タイプに応じて解析を行い、以下の形式の辞書を返す。

    戻り値例:
    {
        "work_history": [
            {"company": ..., "position": ..., "period": ..., "responsibilities": ..., "achievements": ...},
            ...
        ],
        "skills": [
            {"name": ..., "level": ...},
            ...
        ]
    }
    """
    # MIME 判定
    mime = magic.from_buffer(file_bytes, mime=True)

    # テキスト／表データ抽出
    if filename.lower().endswith(".pdf") or mime == "application/pdf":
        text = extract_text(io.BytesIO(file_bytes))
    elif filename.lower().endswith(".docx") or mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = DocxDocument(io.BytesIO(file_bytes))
        text = "\n".join(p.text for p in doc.paragraphs)
    elif filename.lower().endswith(".xlsx") or mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
        # Excel はテーブル形式で返却
        return {"table": df.fillna("").to_dict(orient="records")}
    else:
        # テキストファイル
        text = file_bytes.decode("utf-8", errors="ignore")

    # ----- NLP 解析部分（プロダクションでは実装を差し替え） -----
    # 以下はダミー実装です。
    work_history = [
        {
            "company": "株式会社例",
            "position": "エンジニア",
            "period": "2020-2023",
            "responsibilities": "システム開発",
            "achievements": "売上○%向上"
        }
    ]
    skills = [
        {"name": "Python", "level": "上級"},
        {"name": "TypeScript", "level": "中級"}
    ]

    return {"work_history": work_history, "skills": skills}

# ------------------------------
# Google Sheets 更新ツール
# ------------------------------
@mcp.tool
def update_google_sheet(parsed: Dict[str, Any], spreadsheet_id: str, worksheet_name: str = "Sheet1") -> str:
    """
    parse_document の結果を受け取り、指定スプレッドシートIDのワークシートに書き込む。

    - 職歴: A1～E 列にヘッダー＋データ
    - スキル: G1～H 列にヘッダー＋データ
    """
    # スプレッドシートを開く
    sheet = GS_CLIENT.open_by_key(spreadsheet_id).worksheet(worksheet_name)

    # 職歴ヘッダーとデータ
    header = ["Company", "Position", "Period", "Responsibilities", "Achievements"]
    sheet.update("A1:E1", [header])
    rows = [[
        w.get("company"), w.get("position"), w.get("period"),
        w.get("responsibilities"), w.get("achievements")
    ] for w in parsed.get("work_history", [])]
    if rows:
        sheet.update(f"A2:E{len(rows)+1}", rows)

    # スキルヘッダーとデータ
    skill_header = ["Skill Name", "Level"]
    sheet.update("G1:H1", [skill_header])
    skill_rows = [[s.get("name"), s.get("level")] for s in parsed.get("skills", [])]
    if skill_rows:
        sheet.update(f"G2:H{len(skill_rows)+1}", skill_rows)

    return "Google Sheets を更新しました。"

# ------------------------------
# エントリポイント
# ------------------------------
if __name__ == "__main__":
    mcp.run()
