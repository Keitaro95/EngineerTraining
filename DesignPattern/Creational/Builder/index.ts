// Builder（ビルダー）— 生成パターン
// 目的
// 複雑なオブジェクトの「構築手順」と「表現」を分離し、同じ構築プロセスから異なる表現を作れるようにする。
// 解決する問題
// コンストラクタの引数が増えすぎて、どれが何か分からなくなる状況（いわゆる「テレスコーピング・コンストラクタ」問題）。


// ── 生成物（Product）──
interface HttpRequest {
  method: "GET" | "POST";
  url: string;
  headers: Record<string, string>;
  body?: string;
  timeoutMs: number;
}

// ── Builder ──
class HttpRequestBuilder {
  private method: HttpRequest["method"] = "GET";
  private headers: Record<string, string> = {};
  private body?: string;
  private timeoutMs = 5000;

  constructor(private readonly url: string) {}

  post(): this {
    this.method = "POST";
    return this; // this を返してメソッドチェーンを可能に
  }

  header(key: string, value: string): this {
    this.headers[key] = value;
    return this;
  }

  json(data: unknown): this {
    this.body = JSON.stringify(data);
    return this.header("Content-Type", "application/json");
  }

  timeout(ms: number): this {
    this.timeoutMs = ms;
    return this;
  }

  build(): HttpRequest {
    if (this.method === "GET" && this.body) {
      throw new Error("GET リクエストに body は付けられません");
    }
    return {
      method: this.method,
      url: this.url,
      headers: { ...this.headers },
      body: this.body,
      timeoutMs: this.timeoutMs,
    };
  }
}

// これめっちゃ便利だな。独自のメソッドで見やすく書ける
const req = new HttpRequestBuilder("https://api.example.com/users")
  .post()
  .json({ name: "Alice" })
  .header("Authorization", "Bearer token")
  .timeout(3000)
  .build();