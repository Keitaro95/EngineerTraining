// Composite（コンポジット）パターン

// カテゴリ：構造パターン

// 概要
// 「個々のオブジェクト（Leaf）」と
// 「オブジェクトの集まり（Composite）」を
// 同じインターフェースで扱えるようにするパターンです。
// 木構造（ツリー）を表現し、クライアントは「それが単体か集合か」を意識せずに操作できます。

// 典型例：ファイルシステム（ファイルとディレクトリ）
// GUI部品（ボタンとパネル）、組織図（社員と部署）。

// Component
interface FileSystemNode {
  name: string;
  getSize(): number;
  print(indent?: string): void;
}

// 一つのファイルに関するファイルサイズ：Leaf
class OneFile implements FileSystemNode {
  constructor(public name: string, private size: number) {}

  getSize(): number {
    return this.size;
  }

  print(indent = ""): void {
    console.log(`${indent}📄 ${this.name} (${this.size}KB)`);
  }
}

// Composite
class Directory implements FileSystemNode {
  private children: FileSystemNode[] = [];

  constructor(public name: string) {}

  // pushする
  add(node: FileSystemNode): this {
    this.children.push(node);
    return this;
  }

  // 子に処理を委譲し、結果を集約する
  getSize(): number {
    return this.children.reduce((sum, c) => sum + c.getSize(), 0);
  }

  print(indent = ""): void {
    console.log(`${indent}📁 ${this.name}/`);
    this.children.forEach(c => c.print(indent + "  "));
  }
}

// 利用側
const root = new Directory("src")
  .add(new OneFile("index.ts", 2))
  .add(
    new Directory("components")
      .add(new OneFile("Button.tsx", 5))
      .add(new OneFile("Modal.tsx", 8))
  );

root.print();
console.log(`合計: ${root.getSize()}KB`); // 合計: 15KB