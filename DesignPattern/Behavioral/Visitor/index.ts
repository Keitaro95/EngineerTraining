// ---- Visitor 
// データ構造（要素のクラス群）を変更せずに、
// そこに対する新しい「操作」を後から追加できるようにする。
// 操作を要素クラスの外（Visitor クラス）に切り出し、
// 要素側は accept(visitor) で訪問者を受け入れるだけにする。----
interface ShapeVisitor<R> {
  visitCircle(c: Circle): R;
  visitRectangle(r: Rectangle): R;
}

// ---- Element ----
interface Shape {
  accept<R>(visitor: ShapeVisitor<R>): R;
}

// 円形の時はこれ
class Circle implements Shape {
  constructor(public readonly radius: number) {}
//   ここでアクセプトする 訪問者を受け入れる
  accept<R>(visitor: ShapeVisitor<R>): R {
    return visitor.visitCircle(this); 
  }
}

//正方形の時はこれ
class Rectangle implements Shape {
  constructor(public readonly width: number, public readonly height: number) {}
  accept<R>(visitor: ShapeVisitor<R>): R {
    return visitor.visitRectangle(this);
  }
}

// ---- ConcreteVisitor 1：面積計算 はこれ使う----
class AreaVisitor implements ShapeVisitor<number> {
  visitCircle(c: Circle): number {
    return Math.PI * c.radius ** 2;
  }
  // 正方形の時はこれ使う
  visitRectangle(r: Rectangle): number {
    return r.width * r.height;
  }
}

// ---- ConcreteVisitor 2：SVG 出力（要素クラスは一切変更しない）はこれ使う----
class SvgExportVisitor implements ShapeVisitor<string> {
  visitCircle(c: Circle): string {
    return `<circle r="${c.radius}" />`;
  }
  visitRectangle(r: Rectangle): string {
    return `<rect width="${r.width}" height="${r.height}" />`;
  }
}

// ---- ObjectStructure / 利用側 ----
const shapes: Shape[] = [new Circle(2), new Rectangle(3, 4)];

const area = new AreaVisitor();
const totalArea = shapes.reduce((sum, s) => sum + s.accept(area), 0);
console.log(totalArea.toFixed(2)); // 24.57

const svg = new SvgExportVisitor();
console.log(shapes.map((s) => s.accept(svg)).join("\n"));
// <circle r="2" />
// <rect width="3" height="4" />