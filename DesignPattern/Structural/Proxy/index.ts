// Proxy（プロキシ）パターン — 構造パターン

// 目的：あるオブジェクトへのアクセスを制御するために、その「代理」となるオブジェクトを用意する。クライアントは本物と同じインターフェースの代理を通して操作するので、本物と代理の違いを意識しない。

// 構成要素
// Subject：本物と代理が共通で実装するインターフェース
// RealSubject：実際の処理を行う本物のオブジェクト
// Proxy：RealSubject への参照を持ち、アクセス前後に処理（遅延生成・権限チェック・キャッシュ・ログなど）を挟む

// Subject
interface Image {
  display(): void;
}

// RealSubject：生成にコストがかかる
class HighResImage implements Image {
  constructor(private filename: string) {
    console.log(`ディスクから読み込み中: ${filename}`); // 重い処理
  }
  display(): void {
    console.log(`表示: ${this.filename}`);
  }
}

// 代理：Proxy：初回 display() まで本物を生成しない
class ImageProxy implements Image {
  private real: HighResImage | null = null;

  constructor(private filename: string) {}

  display(): void {
    if (!this.real) {
      this.real = new HighResImage(this.filename); // 遅延生成
    }
    this.real.display();
  }
}

// クライアントは Image としてしか扱わない
const img: Image = new ImageProxy("photo.png");
console.log("プロキシ生成済み（まだ読み込まれていない）");
img.display(); // ここで初めて読み込み → 表示
img.display(); // 2回目は読み込みなし