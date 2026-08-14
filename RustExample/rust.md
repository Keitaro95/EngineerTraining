
https://doc.rust-lang.org/book/title-page.html


https://doc.rust-lang.org/rust-by-example/

```bash
$ rustc hello.rs

$ ./hello
Hello World!

新しいpjを作る（git も同時に追跡される）
cargo new hello_world

src directory にうつして　Cargo.toml fileを作ってもできる.
cargo init
ってしてもいい

cargo build
してから
./target/debug/hello_world　← ビルドの結果がここに入っているかr
または
cargo run

cargo check
だと実行系をしない=バイナリを生成しない
ので早いです
コンパイルだけできます
そのあと 
cargo build
しましょう


適正化したビルド
cargo build --release
これで
target/release 
リリース用のファイルが出てきます
これはビルドは遅いけど、最終的な実行用のバイナリです
```



## 構造体： Structure 

```rs
let m = Meters(5);   // スッキリ
m.0                  // 中身
```


https://doc.rust-lang.org/book/ch01-03-hello-cargo.html#building-and-running-a-cargo-project


https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html


## enum について

```rust
io::stdin()
    .read_line(&mut guess) 
    .expect("Failed to read line");
```

read_line()の返り値に `Result` がある
Result には2つの状態（variant = 変種）がある
「失敗するかもしれない処理」の結果を Result で型として表現します。
いくつかのpossibleなstateを持つタイプをenumと言います

variant（変種） = それぞれの状態（Result なら Ok と Err）
Ok(value)	処理が成功。中に結果の値が入っている
Err(error)	処理が失敗。中にエラー情報が入っている


で、このenum `Result` は expectメソッドを持っています
.expect("Failed to read line") 
Ok なら → 中の値を取り出して処理を続行
Err なら → プログラムを止めて "Failed to read line" というメッセージを表示


6/28 21:38
https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html#printing-values-with-println-placeholders


## Increasing Functionality with a Crate
https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html#increasing-functionality-with-a-crate

乱数生成は crate を使いましょう
- バイナリコードであり実行可能な crate = 今 cargo run で作ったやつ
- `rand` crate ＝　単独では実行できず、他で使われるための crate

Cargo.toml の 依存関係に追加
その後
cargo build
これで Crates.io　からDLされる
Cargo.lockファイルを生成して
次に cargo build する時には Cargo.lock ファイルを見る

`cargo update` で lockファイルを無視して dependencyに書いてある通りのこと更新する → Cargo.lockファイルを更新する


https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html#generating-a-random-number



`cargo doc --open` で 依存関係に追加した docを生成して開く


https://doc.rust-lang.org/book/ch02-00-guessing-game-tutorial.html#allowing-multiple-guesses-with-looping


### 3.2
https://doc.rust-lang.org/book/ch03-02-data-types.html


```rust
let guess: u32 = "42".parse().expect("Not a number!")


```

signed は符号あり
unsigined は符号なし

```rust
i8：-128 ～ 127
u8：0〜255

57u8：57をu8型で書く
let a = 57u8;

let a =0xffu8;
let a =225u8;

1_000は1000
1_000_000_000


fn main() {
    let x = 2.0;

    let y: f32 = 3.0;

    let t = true;

    let f: bool = false;

    let z: char = 'Z'

    let tup: (i32, f64, u8) = (500, 6.4, 1)
}
```


## 所有権：Ownership

### スタック = 先入後だし
aを先に入れているが　Cを先に出す
こうすると、アロケートした場所を機にする必要がないのでメモリ効率がいい
スタック上のデータを扱う方が、データの位置をポインタをわざわざ辿る必要がないので
処理が早い
|  C |
|  B |
|  A |

### ヒープ = メモリの空間を割り当てて、場所を記憶しておく
データを格納する一定の場所を見つけて
場所を覚えておく（ポインタ）
ポインタを辿るため、スタックより遅くなる


関数に渡す値・関数のlocal変数
↓ スタックにpushする
関数が処理をする
↓
処理が終わったらpopする


ヒープに
データを保存しているよね。
その中で、同じ値を保存しているなら
**データの重複を最小限に抑える**
（できるだけ同じデータ・同じポインタ使って参照させること）

**ヒープの未使用データをクリーンアップする**

Ownership 所有権はこれらを考えなくする仕組みだけど、***中では heapデータの管理が目的だよ***


## ownershipについて

- 値はオーナーを持つ
- オーナーは1度に一人
- オーナースコープを外れると値は棄却される



https://doc.rust-lang.org/book/ch05-03-method-syntax.html



https://doc.rust-lang.org/book/ch06-02-match.html#the-optiont-match-pattern


https://claude.ai/chat/35e9fe18-5dfe-4ec5-85a8-63a3757982fa


パッケージ
- Cargo.toml
- ライブラリクレート 0~1こ 実際の機能は全てここに定義する
    クレートルート：src/lib.rs　
        ここにモジュールツリーを書く
```rust
mod front_of_house { 接客フロア：客席側、親だから、子供の中身は見られない
    mod hosting { 案内係：バックオフィス、子であり、親を除くことができる
        fn add_to_waitlist() {}
        fn seat_at_table() {}
    }
    mod serving {　給仕係
        fn take_order() {}
        fn serve_order() {}
        fn take_payment() {}
    }
}
```
- バイナリクレート 好きなだけ作れる。実行可能ファイルに必要な最小限のコード
        この中でモジュールツリーのパッケージ名からパスを始める
    クレートルート：src/main.rs
    そのほか：src/bin/


backyard
- Cargo.lock
- Cargo.toml
- src
    - garden
        - vegetables.rs
    - garden.rs
    - main.rs

```rust
use crate::garden::vegetables::Asparagus;

// gardenファイルの中全部含めてね、とコンパイラに伝えてる
pub mod garden;

fn main() {
    let plant = Asparagus {};
    println!("I'm growing {plant:?}!");
}
```




呼び出す時は　`crate::front_of_house::hosting`


```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {

    crate::front_of_house::hosting::add_to_waitlist();

    front_of_house::hosting::add_to_waitlist();
}
```

基本は子モジュールは先祖のモジュールのアイテムを使えるけど
先祖からはモジュールを使えない

代わりに pub　を使えば　必要な部分だけ公開できる


```rust
mod front_of_house {
    pub mod hosting {
        fn add_to_waitlist() {}
    }
}
```

```rust
// これだと hostingの存在を参照できるけど中身まで公開されない
mod front_of_house {
    pub mod hosting {
        fn add_to_waitlist() {}
    }
}
```


```rust
// これでやっと関数の中身も公開される
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}
```


相対パスで書くとこうなる

crate → front_of_house(兄弟なのでOK) → hosting(pub必要) → add_to_waitlist(pub必要)

```rust
front_of_house::hosting::add_to_waitlist();
```





```rust
fn deliver_order() {} ← crate直下 back_of_houseの親

mod back_of_house {
    fn fix_incorrect_order() {
        cook_order();
        super::deliver_order(); ←親(crate)に上がってから deliver_orderを探す
    }
    fn cook_order() {}
}
```

まとめ：絶対パス・相対パス・super の使い分け感覚
crate::...          → 常にルートから正確な位置を指定（構造の全体像が固定的なとき）
front_of_house::...  → 現在地からの相対（兄弟モジュールなど、近くの関係を表す）
super::...           → 親モジュールへ「一段階だけ」上がる（親子の結びつきが強いとき）


```rust
mod back_of_house {
    pub struct Breakfast {
        pub toast: String, 
        seasonal_fruit: String, // 何もつけなければ private
    }

    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}

pub fn eat_at_restaurant() {
    let mut meal = back_of_house::Breakfast::summer("Rye");

    meal.toast = String::from("Wheat");
    println!("I'd like {} toast please", meal.toast);


}

mod back_of_house {
    pub enum Appetizer {
        Soup,
        Salad,
    }
}
pub fn eat_at_restaurant() {
    let order1 = back_of_house::Appetizer::Soup;
    let order2 = back_of_house::Appetizer::Salad;
}
```


src/lib.rs
```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

// useを使って呼びだすと、そのスコープではhostingという名前が有効な名前になる
// クレートルートのスコープでの use
use crate::front_of_house::hosting;

// 関数の中で使える
pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}

// ここは customer モジュールのスコープにあるので
// rootのuseはここには効かない
mod customer {
    pub fn eat_at_restaurant() {
        hosting::add_to_waitlist();
    }
}
```


src/main.rs
```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::new();
    map.insert(1, 2);
}

``` 

src/lib.rs
```rust
use std::fmt::Result;
use std::io::Result as IoResult; // as インポート

fn function1() -> Result {
    // --snip--
}

fn function2() -> IoResult<()> {
    // --snip--
}
```


```rust
src/lib.rs
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}
```
`restaurant::front_of_house::hosting::add_to_waitlist();`
↓ こう書くところを省略できる
`restaurant::front_of_house::hosting::add_to_waitlist();`


変更後（pub use で hosting をルートモジュールから再エクスポート）
では、外部コードはこう書けます。
rustrestaurant::hosting::add_to_waitlist();
front_of_house という内部の階層を経由せず、あたかも hosting がクレートルート直下に定義されているかのように外部から見える、というわけです。


```rust
use std::collections::HashMap;

fn main() {
    let secret_number = rand::thread_rng().gen_range(1..=100);
}
```


```rust
use std::cmp::Ordering;
use std::io;

こう書いてもいい
use std::{cmp::Ordering, io};


use std::io;
use std::io::Write;

use std::io::{self, Write};

```