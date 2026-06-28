# Formatting（フォーマット）

ここまで見てきたように、フォーマット（書式）は中かっこ `{}` を使った文字列の指定で行います。中かっこの中身を書き換えることで、テキストを「同じ位置に置き換える（プレースホルダ）」だけでなく、表示のされ方を細かく指定できます。

フォーマットの正しさ（どんな引数が必要か、どんな型が使えるか）は、コンパイル時にチェックされます。

これまでも、いくつかのフォーマット指定を見てきました。

- `{}` … 引数を自動で適切な形に整形する（`fmt::Display` を使う）。
- `{:?}` … デバッグ用の整形（`fmt::Debug` を使う）。
- `{:#?}` … きれいに整形したデバッグ出力（pretty debug）。

## さまざまなフォーマット指定の例

`std::fmt` には多くのトレイトがあり、出力の仕方を制御します。代表的なものは次の2つです。

- `fmt::Display` … `{}` のマーカーで出力する。テキストとして読みやすい形式。
- `fmt::Debug` … `{:?}` のマーカーで出力する。デバッグに使う形式。

ここでは、日付を `YYYY-MM-DD` の形式で表示する例を見てみます。

```rust
use std::fmt::{self, Formatter, Display};

struct City {
    name: &'static str,
    // 緯度（latitude）
    lat: f32,
    // 経度（longitude）
    lon: f32,
}

impl Display for City {
    // `f` は出力先のバッファ。このメソッドは、
    // 整形した文字列を `f` に書き込まなければならない。
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        let lat_c = if self.lat >= 0.0 { 'N' } else { 'S' };
        let lon_c = if self.lon >= 0.0 { 'E' } else { 'W' };

        // `write!` は `format!` と似ているが、整形した文字列を
        // バッファ（最初の引数 `f`）に書き込む点が違う。
        write!(f, "{}: {:.3}°{} {:.3}°{}",
               self.name, self.lat.abs(), lat_c, self.lon.abs(), lon_c)
    }
}

#[derive(Debug)]
struct Color {
    red: u8,
    green: u8,
    blue: u8,
}

fn main() {
    for city in [
        City { name: "Dublin", lat: 53.347778, lon: -6.259722 },
        City { name: "Oslo", lat: 59.95, lon: 10.75 },
        City { name: "Vancouver", lat: 49.25, lon: -123.1 },
    ] {
        println!("{}", city);
    }
    for color in [
        Color { red: 128, green: 255, blue: 90 },
        Color { red: 0, green: 3, blue: 254 },
        Color { red: 0, green: 0, blue: 0 },
    ] {
        // `{}` で表示できるように、`Display` の実装を追加してみよう。
        println!("{:?}", color);
    }
}
```

## よく使うフォーマット指定子

中かっこの中の `:` の後ろに、表示方法を細かく指定できます。

| 指定 | 意味 |
|------|------|
| `{:.3}` | 小数点以下3桁で表示する（精度の指定） |
| `{:5}` | 最低5文字幅を確保して右寄せ（数値の場合） |
| `{:<5}` | 幅5で左寄せ |
| `{:>5}` | 幅5で右寄せ |
| `{:^5}` | 幅5で中央寄せ |
| `{:05}` | 幅5でゼロ埋め |
| `{:b}` | 2進数（`fmt::Binary`） |
| `{:o}` | 8進数 |
| `{:x}` / `{:X}` | 16進数（小文字 / 大文字） |
| `{:+}` | 正の数にも符号を付ける |

## 演習（チャレンジ）

1. 上のプログラムに `Color` 構造体用の `fmt::Display` を実装し、次のような出力にしてみましょう。

   ```
   RGB (128, 255, 90) 0x80FF5A
   RGB (0, 3, 254) 0x0003FE
   RGB (0, 0, 0) 0x000000
   ```

   ヒント：各色を16進数で表示するには `{:02X}`（2桁・ゼロ埋め・大文字）を使うとうまくいきます。

## ポイント整理

- `{}` は `Display`、`{:?}` は `Debug`、`{:#?}` は pretty debug。
- `:` の後ろで幅・精度・進数・寄せ方などを指定する。
- `write!(f, ...)` はバッファ `f` に書き込み、`format!` は文字列を作って返す。
- フォーマットの正しさはコンパイル時に検査される。

## 参考

- `std::fmt`

---

> 出典: 本教材は [Rust by Example - Formatting](https://doc.rust-lang.org/rust-by-example/hello/print/fmt.html)（MIT / Apache-2.0 ライセンス）を基に日本語で再構成したものです。
