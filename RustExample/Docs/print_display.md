# Display

`fmt::Debug` は見た目がきれいとは言えません。出力の見た目を自分でカスタマイズしたい場合は、`fmt::Display` トレイトを手動で実装します。`fmt::Display` は `{}` というマーカーを使って出力します。実装の仕方は次のようになります。

```rust
// `fmt` をインポートして、`fmt::Display` を使えるようにする。
use std::fmt;

// `fmt::Display` を実装したい構造体を定義する。
// この `Structure` は `i32` を1つ持つタプル構造体。
struct Structure(i32);

// `Structure` に `fmt::Display` を実装するために、
// `impl` ブロックを使う。
impl fmt::Display for Structure {
    // このトレイトでは `fmt` というメソッドを実装する必要があり、
    // シグネチャは正確にこの形でなければならない。
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // 最初の要素を、与えられた出力ストリーム `f` に書き込む。
        // `write!` は `println!` とよく似た使い方で、結果として
        // `fmt::Result` を返す。
        write!(f, "{}", self.0)
    }
}
```

`fmt::Display` は `fmt::Debug` よりもきれいに出力できますが、`std` ライブラリにとっては困った面もあります。曖昧な型（あいまいな型）はどう表示すればよいのでしょうか？ たとえば `std` ライブラリが、すべての `Vec<T>`（あらゆる `T` を持つベクタ）に対して画一的なスタイルを実装してしまうと、その表示形式は本当に明確でしょうか？ おそらく、すべての場面に合うわけではありません。

そのため、`std` ライブラリでは一般的な汎用コンテナに対して `fmt::Display` を実装していません。そうした汎用型では `fmt::Debug` を使う必要があります。

ただし、汎用ではない「新しいコンテナ型」を自分で作る場合は、`fmt::Display` を実装して構いません。問題は起きません。

```rust
use std::fmt; // `fmt` をインポート

// 2つの数値を持つ構造体。`Debug` を導出して、
// `Display` と出力を比較できるようにする。
#[derive(Debug)]
struct MinMax(i64, i64);

// `MinMax` に `Display` を実装する。
impl fmt::Display for MinMax {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // 構造体の中身（フィールド）を指定して書き込む。
        // `self.0` で最初の、`self.1` で2番目のフィールドにアクセスする。
        write!(f, "({}, {})", self.0, self.1)
    }
}

// 名前付きフィールドを持つ構造体（比較のため）。
#[derive(Debug)]
struct Point2D {
    x: f64,
    y: f64,
}

// 同じように `Point2D` にも `Display` を実装する。
impl fmt::Display for Point2D {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // `x` と `y` だけを使って表示する。
        write!(f, "x: {}, y: {}", self.x, self.y)
    }
}

fn main() {
    let minmax = MinMax(0, 14);

    println!("Compare structures:");
    println!("Display: {}", minmax);
    println!("Debug: {:?}", minmax);

    let big_range =   MinMax(-300, 300);
    let small_range = MinMax(-3, 3);

    println!("The big range is {big} and the small is {small}",
             small = small_range,
             big = big_range);

    let point = Point2D { x: 3.3, y: 7.2 };

    println!("Compare points:");
    println!("Display: {}", point);
    println!("Debug: {:?}", point);

    // エラーになる例。`Debug` も `Display` も実装されているが、
    // `{:b}`（2進数フォーマット）には `fmt::Binary` の実装が必要。
    // これは動かない。
    // println!("What does Point2D look like in binary: {:b}?", point);
}
```

## ポイント整理

- `{}` … `fmt::Display` を使った出力。表示形式を自分でカスタマイズできる。
- `impl fmt::Display for 型名 { ... }` で実装する。
- 実装するメソッドは `fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result`。
- 中身の書き込みには `write!(f, ...)` を使う。
- `std` の汎用コンテナ（`Vec<T>` など）は `Display` を実装していないので `{:?}` を使う。

## まとめ

`fmt::Display` は実装したものの、`{:b}`（2進数）のような他のフォーマット指定には対応していません。
そうしたフォーマットには、それぞれ対応するトレイト（`fmt::Binary` など）の実装が必要です。

## 参考

- `derive`、`std::fmt`、マクロ（macros）、`struct`、トレイト（trait）、`use`

---

> 出典: 本教材は [Rust by Example - Display](https://doc.rust-lang.org/rust-by-example/hello/print/print_display.html)（MIT / Apache-2.0 ライセンス）を基に日本語で再構成したものです。
