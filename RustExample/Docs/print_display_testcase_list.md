# テストケース：List（リストの表示）

構造体の各要素を順番に処理しながら `fmt::Display` を実装するのは、なかなか手強い課題です。問題は、`write!` を1回呼び出すごとに `fmt::Result` が返ってくることです。これを正しく処理するには、すべての結果（Result）を扱わなければなりません。Rust では、まさにこの目的のために `?` 演算子（オペレータ）が用意されています。

`?` を `write!` に対して使うと、次のように動作します。

```rust
// `write!` を実行し、エラーが起きたかどうかを調べる。
// エラーなら、そのエラーを返す（return）。
// エラーでなければ、そのまま処理を続ける。
write!(f, "{}", value)?;
```

`?` 演算子を使えば、ベクタ（`Vec`）の各要素を `Display` で表示する実装も比較的すっきり書けます。

```rust
use std::fmt; // `fmt` をインポート

// `Vec`（ベクタ）を持つ構造体 `List` を定義する。
struct List(Vec<i32>);

impl fmt::Display for List {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // タプル構造体の中のベクタにインデックスでアクセスし、
        // それを `vec` という参照で束縛する。
        let vec = &self.0;

        write!(f, "[")?;

        // `vec` の各要素を反復処理する。番号（カウント）も `iter` から取得する。
        for (count, v) in vec.iter().enumerate() {
            // 最初の要素以外には、先頭にカンマを付ける。
            // `?` を使ってエラーが起きたら return する。
            if count != 0 { write!(f, ", ")?; }
            write!(f, "{}", v)?;
        }

        // 開いた角かっこを閉じて、結果（fmt::Result）を返す。
        write!(f, "]")
    }
}

fn main() {
    let v = List(vec![1, 2, 3]);
    println!("{}", v);
}
```

実行結果は次のとおりです。

```
[1, 2, 3]
```

## 演習（チャレンジ）

このプログラムを変更して、ベクタの各要素のインデックス（添字）も一緒に表示してみましょう。

期待する出力例：

```
[0: 1, 1: 2, 2: 3]
```

ヒント：`enumerate()` で取得した `count` を、そのままインデックスとして使えます。

```rust
// 変更後の write! の例
write!(f, "{}: {}", count, v)?;
```

## ポイント整理

- `?` 演算子 … `Result` を返す処理でエラーが起きたら即座に return し、成功なら続行する。
- `vec.iter().enumerate()` … 各要素を「(連番, 値)」のペアとして反復できる。
- `&self.0` でタプル構造体の中身を参照として取り出す。

## 参考

- `for` ループ、`ref`、`Result`、`struct`、`?` 演算子、`Vec`

---

> 出典: 本教材は [Rust by Example - Testcase: List](https://doc.rust-lang.org/rust-by-example/hello/print/print_display/testcase_list.html)（MIT / Apache-2.0 ライセンス）を基に日本語で再構成したものです。
