// Flyweight（フライウェイト）パターン — 構造パターン

// 目的：大量のオブジェクトを扱うとき、共有可能な状態（内部状態）を
// 1つのインスタンスにまとめて共有し、
// 個別に異なる状態（外部状態）は外から渡すことでメモリ消費を抑える。

// 典型例：テキストエディタの文字（グリフ）、ゲームの木や弾丸、地図のマーカーなど。



// 内部状態（共有されるので一つにまとめる）: 種類・色・テクスチャ
class TreeType {
    constructor(
        readonly name: string,
        readonly color: string,
        readonly texture: string,
    ) {}

    draw(x: number, y: number): void {
        console.log(`${this.name}(${this.color}) を (${x}, ${y} に描画)`);
    }
}

// Treeを作る工場 色違いであってもこの工場を経由して作る
class TreeFactory {
  private static types = new Map<string, TreeType>();

  static get(name: string, color: string, texture: string): TreeType {
    const key = `${name}_${color}_${texture}`;
    if (!this.types.has(key)) {
      this.types.set(key, new TreeType(name, color, texture));
    }
    return this.types.get(key)!;
  }

  static get count(): number {
    return this.types.size;
  }
}

// 木はこうやって作るよ
class Tree {
    constructor(
        private x: number,
        private y: number,
        private type: TreeType,
    ) {}

    draw(): void {
        this.type.draw(this.x, this.y);
    }
}


// 森はこうやって作るよ
class Forest {
    private trees: Tree[] = [];

    plant(x: number, y: number, name: string, color: string, texture: string): void {
    const type = TreeFactory.get(name, color, texture);
    this.trees.push(new Tree(x, y, type));
  }

  draw(): void {
    this.trees.forEach((t) => t.draw());
  }
}


// これめっちゃ面白いな!!
// ゲームってこう作られてるんだ!!!
const forest = new Forest();
for (let i = 0; i < 10_000; i++) {
    forest.plant(Math.random() * 1000, Math.random() * 1000, "松", "緑", "pine.png");
  forest.plant(Math.random() * 1000, Math.random() * 1000, "桜", "桃", "sakura.png");
}
console.log(`木の数: 20000, TreeType インスタンス数: ${TreeFactory.count}`); // → 2


