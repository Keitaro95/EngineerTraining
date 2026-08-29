// Singleton（シングルトン）— 生成パターン

// 目的：クラスのインスタンスが1つしか存在しないことを保証し、それへのグローバルなアクセス点を提供する。

// 典型的な用途：設定情報、ロガー、DB接続プール、キャッシュなど「システム全体で1つ」であるべきもの。

class Config {
  private static instance: Config | null = null;
  private settings = new Map<string, string>();

  // 外部から new できないようにする
  private constructor() {
    this.settings.set("env", "production");
  }

  static getInstance(): Config {
    if (Config.instance === null) {
      Config.instance = new Config();
    }
    return Config.instance;
  }

  get(key: string): string | undefined {
    return this.settings.get(key);
  }
}

const a = Config.getInstance();
const b = Config.getInstance();
console.log(a === b); // true — 同一インスタンス
// new Config(); // コンパイルエラー：コンストラクタは private
