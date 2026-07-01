
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