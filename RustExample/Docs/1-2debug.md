# Debug（デバッグ出力）

`std::fmt` のフォーマット用トレイト（`fmt::Debug` や `fmt::Display`）を使って型を出力するには、それぞれのトレイトを実装する必要があります。`std` ライブラリの多くの型には、これらの実装が最初から用意されています。一方で、自分で定義した型については、自分で実装しなければなりません。

`fmt::Debug` トレイトは、この実装をとても簡単にしてくれます。**ほぼすべての型** は `fmt::Debug` を自動で導出（derive）できます。`fmt::Display` ではこれができず、手動で実装する必要があります。

```rust
// この構造体は `fmt::Display` でも `fmt::Debug` でも出力できない。
struct UnPrintable(i32);

// `derive` 属性を付けると、この構造体を
// `fmt::Debug` で出力できるようにする実装が自動生成される。
#[derive(Debug)]
struct DebugPrintable(i32);
```

## 自動導出（derive）

すべての `std` ライブラリの型も、`{:?}` を使って自動で出力できます。

```rust
// `Structure` という構造体に `i32` を1つ入れる。
#[derive(Debug)]
struct Structure(i32);

// `Structure` を `Deep` という構造体の中に入れる。これも
// 出力可能にする。
#[derive(Debug)]
struct Deep(Structure);

fn main() {
    // `{:?}` を使った出力は `{}` とよく似ている。
    println!("{:?} months in a year.", 12);
    println!("{1:?} {0:?} is the {actor:?} name.",
             "Slater",
             "Christian",
             actor="Actor's");

    // `Structure` 型も出力できるようになった！
    println!("Now {:?} will print!", Structure(3));

    // `derive` を使う場合の問題点は、出力結果の見た目を
    // こちら側で制御できないことだ。
    // この `7` だけを表示したい場合はどうすればいいだろう？
    println!("Now {:?} will print!", Deep(Structure(7)));
}
```

`fmt::Debug` を使えば、確かに「出力できる」ようになります。しかし、見た目の美しさは犠牲になります。Rust では `{:#?}` を使うことで「整形された（pretty）」出力も可能です。

```rust
#[derive(Debug)]
struct Person<'a> {
    name: &'a str,
    age: u8
}

fn main() {
    let name = "Peter";
    let age = 27;
    let peter = Person { name, age };

    // 整形された（pretty）出力。
    println!("{:#?}", peter);
}
```

実行結果は次のようになります。

```
Person {
    name: "Peter",
    age: 27,
}
```

## ポイント整理

- `{:?}` … `fmt::Debug` を使った出力。
- `{:#?}` … 整形された（pretty）`fmt::Debug` 出力。
- `#[derive(Debug)]` … 構造体や列挙型に付けると、`fmt::Debug` の実装が自動生成される。
- 出力の見た目を細かく制御したい場合は、`fmt::Display` を手動で実装する。

## まとめ

`fmt::Display` を手動で実装すれば、表示方法を自分で制御できます。
このトピックについては、次のセクション「Display」で詳しく学びます。

## 参考

- 属性（attributes）、`derive`、`std::fmt`、構造体（structs）

---

> 出典: 本教材は [Rust by Example - Debug](https://doc.rust-lang.org/rust-by-example/hello/print/print_debug.html)（MIT / Apache-2.0 ライセンス）を基に日本語で再構成したものです。
