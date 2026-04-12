



## セクション8: ログ設計とOpenAPIドキュメント本番設定
Python標準loggingとFastAPIの関係
FastAPIは独自のログシステムを持たず、Python標準のloggingモジュールに依存する。Uvicornはuvicorn（汎用）とuvicorn.access（アクセスログ）の2つのロガーを使用する。アプリケーションコードのログは開発者が明示的に設定する必要がある。
structlogによる構造化ログの実装
structlogはプロセッサチェーンでログイベントを順次変換する。各プロセッサはログイベント辞書を受け取り、加工して次に渡す。本番ではJSON出力、開発ではカラー付きコンソール出力を切り替えるのが定石だ。

承知いたしました。ご提示いただいたstructlogによる構造化ログ設定のコードから空行を削除し、整形しました。
import structlog
import logging
import sys
def configure_logging(json_logs: bool = True, log_level: str = "INFO"):
    shared_processors = [
        structlog.contextvars.merge_contextvars,     # コンテキスト変数のマージ
        structlog.stdlib.add_log_level,              # ログレベル追加
        structlog.processors.TimeStamper(fmt="iso", utc=True),  # ISO時刻
        structlog.processors.format_exc_info,         # 例外フォーマット
    ]
    renderer = (structlog.processors.JSONRenderer() if json_logs
                else structlog.dev.ConsoleRenderer(colors=True))
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
    # ノイズの多いロガーを抑制
    for name in ["uvicorn", "uvicorn.access", "httpx"]:
        logging.getLogger(name).setLevel(logging.WARNING)
補足情報：structlogの動作

この設定は、structlogのプロセッサチェーンを利用してログイベントを構造化し、本番環境ではJSONRendererによるJSON出力、開発環境ではカラー付きのコンソール出力を切り替えるためのものです。また、uvicornやhttpxなどのライブラリから発生する大量のログをWARNINGレベルに抑制しています。

相関ID（Correlation ID）のミドルウェア実装
リクエストごとに一意のIDを割り当て、全ログに含めることでマイクロサービス間のトレースを可能にする。contextvarsを使ってリクエストスコープの値を保持する。

承知いたしました。ご提示いただいた相関ID（Correlation ID）のミドルウェアコードから空行を削除し、整形しました。
from contextvars import ContextVar
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # クライアントが送信したIDを優先、なければ生成
        cid = request.headers.get("X-Correlation-ID") or uuid4().hex
        correlation_id_var.set(cid)
        structlog.contextvars.bind_contextvars(correlation_id=cid)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response
補足情報：相関IDの用途

このミドルウェアは、リクエストごとに一意のIDを割り当て、
contextvars
を使ってリクエストスコープの値を保持することで、マイクロサービス間のトレースを可能にします。

なお、ドキュメントでは、本番環境での使用には
asgi-correlation-id
パッケージの使用が推奨されており、
structlog
の
contextvars
と組み合わせることで、全ログに自動的に相関IDが含まれるようになります。


本番ではasgi-correlation-idパッケージ（https://github.com/snok/asgi-correlation-id ）の使用が推奨される。structlogのcontextvarsと組み合わせれば、全ログに自動的に相関IDが含まれる。
