// Adapter（アダプター）パターン — 構造パターン

// 目的：インターフェースが合わないクラスを、クライアントが期待するインターフェースに変換して再利用できるようにする。電源プラグの変換アダプターと同じ発想です。

// 登場人物

// Target：クライアントが使いたいインターフェース
// Adaptee：既存の、インターフェースが合わないクラス
// Adapter：Target を実装し、内部で Adaptee を呼び出す
// Client：Target だけを見て動く


// Target：クライアントが期待するインターフェース
interface Logger {
  log(level: "info" | "error", message: string): void;
}

// Adaptee：既存の外部ライブラリ（変更できない）
class LegacyLogger {
  writeInfo(text: string): void { console.log(`[INFO] ${text}`); }
  writeError(text: string, code: number): void { console.error(`[ERR ${code}] ${text}`); }
}

// Adapter：Target Loggerに対して実装し、Adaptee に委譲する（オブジェクトアダプター）
class LegacyLoggerAdapter implements Logger {
  constructor(private readonly legacy: LegacyLogger) {}

  log(level: "info" | "error", message: string): void {
    if (level === "info") this.legacy.writeInfo(message);
    else this.legacy.writeError(message, 500);
  }
}

// Client：Logger しか知らない
function processOrder(logger: Logger): void {
  logger.log("info", "注文を処理しました");
  logger.log("error", "在庫が不足しています");
}

processOrder(new LegacyLoggerAdapter(new LegacyLogger()));