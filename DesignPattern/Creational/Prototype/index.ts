// Prototype パターン（生成に関するパターン）
// 目的：既存のインスタンスを「原型（prototype）」として複製し、新しいオブジェクトを生成する。new でクラスから作るのではなく、オブジェクト自身が自分のコピーを返すのが特徴です。
// 使いどころ
// 生成コストが高い（初期化に計算やI/Oが必要）オブジェクトを何度も作りたい
// 実行時に生成するクラスが決まる／クラス階層をクライアントから隠したい
// 状態が少しずつ違うバリエーションを大量に作りたい（ゲームのユニット、図形エディタなど）

interface Prototype<T> {
  clone(): T;
}

class Shape implements Prototype<Shape> {
  constructor(
    public x: number,
    public y: number,
    public color: string,
    public tags: string[] = [],
  ) {}

  clone(): Shape {
    // ディープコピー（配列を共有しないように注意）
    return new Shape(this.x, this.y, this.color, [...this.tags]);
  }
}

// 原型を登録しておくレジストリ（よくある組み合わせ）
class ShapeRegistry {
  private prototypes = new Map<string, Shape>();
  register(key: string, proto: Shape) { this.prototypes.set(key, proto); }
  create(key: string): Shape {
    const p = this.prototypes.get(key);
    if (!p) throw new Error(`unknown prototype: ${key}`);
    return p.clone();
  }
}

// --- 利用側 ---
const registry = new ShapeRegistry();

// 新しい機能を追加
registry.register("redCircle", new Shape(0, 0, "red", ["circle"]));

const c1 = registry.create("redCircle");
const c2 = registry.create("redCircle");
c2.x = 100;
c2.tags.push("moved");

console.log(c1); // Shape { x: 0,   y: 0, color: 'red', tags: ['circle'] }
console.log(c2); // Shape { x: 100, y: 0, color: 'red', tags: ['circle','moved'] }