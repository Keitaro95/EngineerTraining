
https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html#the-string-type



```rust
{                       // ここで　s は効かない
    let s = "s";    // ここで　s は効く
                        // ここで　s は効く
}                       // scopeは外れている、over


// String typeの下に fromという名前空間　をとって、　関連関数from　を呼ぶ。
let s = String::from("hello");

s.push_str(", world!"); 

println!("{s}");

```