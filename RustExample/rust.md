
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

