
// レンダラーのinterface
interface Renderer {
    drawCircle(x: number, y: number, r: number): void;
}

// svg描画のレンダラー
class SvgRenderer implements Renderer {
    drawCircle(x: number, y: number, r: number) {
        console.log(`<circle cx="${x} cy="${y}" />`)
    }
}
// canvas描画のレンダラー
class CanvasRenderer implements Renderer {
    drawCircle(x: number, y: number, r: number) {
        console.log(`ctx.arc(${x}, ${y}, ${r}, 0, Math.PI * 2)`);
    }
}


// Abstraction ：Shapeの抽象クラス。このinterfaceがあるおかげで、変数の渡し方を統一できる
abstract class Shape {
  constructor(protected renderer: Renderer) {} // ← ここが「橋」
  abstract draw(): void;
}

// レンダラのクラスに関わらず統一された動きを定義する
// 選ぶレンダらによって振る舞いを変えることができる
class Circle extends Shape {
  constructor(renderer: Renderer, private x: number, private y: number, private r: number) {
    super(renderer);
  }
  draw() {
    // drawCircleを実行。振る舞いは使うレンダラーで変わる
    this.renderer.drawCircle(this.x, this.y, this.r);
  }
  scale(factor: number) { this.r *= factor; }
}

const c1 = new Circle(new SvgRenderer(), 10, 10, 5);
const c2 = new Circle(new CanvasRenderer(), 10, 10, 5);
c1.draw();
c2.draw();