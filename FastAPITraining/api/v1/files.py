from fastapi import APIRouter
from fastapi.responses import Response

from utils.files import get_file_size

router = APIRouter(
    prefix="/files",
    tags=["files"], # swaggerに出るよ
    # dependencies=[Depends(require_admin)] # この router固有の依存性
)
"""
ファイルがサーバーにあるか確認するよ
ダウンロード前のサイズ確認とか
プログレスバー表示
"""
@router.head("/files/{file_id}")
async def head_file(file_id: int):
    file_size = get_file_size(file_id)
    return Response(
        headers={
            "Content-Length": str(file_size),
            "Content-Type": "application/octet-stream",
            "X-File-Exists": "true",
        }
    )




