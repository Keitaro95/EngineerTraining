// Decorator（デコレーター）パターン

// 分類：構造パターン（Structural）
// 目的：オブジェクトに対して、サブクラス化を使わずに動的に責務（機能）を追加する。

// 考え方
// 元のオブジェクトを「包む（wrap）」オブジェクトを作り、
// 同じインターフェースを実装させます。
// 包む側は処理の前後に独自の振る舞いを追加し、
// 本体の処理は内側のオブジェクトへ委譲します。包む層をいくつでも重ねられるので、
// 機能の組み合わせが継承よりはるかに柔軟になります。

// 飲み物 抽象クラス
interface Beverage {
    description(): string;
    cost(): number;
}

// ConcreteComponent: 本体　はコーヒー
class Coffee implements Beverage {
  description() { return "コーヒー"; }
  cost() { return 300; }
}

// Decorator: 共通の抽象クラス（内側の Beverage を保持して委譲する）　デコりましょう
abstract class BeverageDecorator implements Beverage {
  constructor(protected readonly inner: Beverage) {}
  description() { return this.inner.description(); }
  cost() { return this.inner.cost(); }
}

// ConcreteDecorator: 機能を付け足す　ミルクを足しましょう
class Milk extends BeverageDecorator {
  description() { return `${this.inner.description()} + ミルク`; }
  cost() { return this.inner.cost() + 50; }
}

// ホイップを足しましょう
class Whip extends BeverageDecorator {
  description() { return `${this.inner.description()} + ホイップ`; }
  cost() { return this.inner.cost() + 80; }
}

const order: Beverage = new Whip(new Milk((new Coffee())))
console.log(order.description()); // コーヒー + ミルク + ミルク + ホイップ
console.log(order.cost());        // 480