fn main() {

    // stringりてらるは早いけど、immutableだから早いだけ

    // サイズがわからないし、プログラムの中で、値を変えるテキストのようなバイナリに
    // メモリを割り当てることはできない。つまり、 mutableなものに適切にメモリ空間を与えられない。
    {                       // ここで　s は効かない
        let s = "s";    // ここで　s は効く
                            // ここで　s は効く
    }                       // scopeは外れている、over


    // なので、 mutable な値にメモリを割り当てるにはヒープにそれなりのメモリを割り当てる必要がある

    // runtime時に、メモリアロケーターから、メモリが要求される

    // そして String空間で使用が終わったら、終わったことをメモリアロケーターにこのメモリを返す必要がある

    // String typeの下に fromという名前空間　をとって、　関連関数from　を呼ぶ。
    // これは mutateできる

    // String::fromで メモリをよぶ。ガーベジコレクションに、使わなくなったメモリを掃き溜めにしておける
    // でもこれ難しい、使わない変数のメモリは解放して、使うものは持っておいて...
    だから、Rustは、scopeを出たら 自動的にメモリをリターン、捨てる機構を持っている
    {
        let s = String::from("hello"); // ここで　s は効く
        // ここで　s は効く
    } // scopeは外れている、over → Rust は　dropする。Rust の drop機能が働く
    // =これはC++のRAIIににている

    let mut s = String::from("hello");

    s.push_str(", world!"); 

    println!("{s}");


    複雑な例を見てみます

    let x = 5; xに5をbindする
    let y = x; xのcopyを作ってyにbindする
    これら2つの5は stackにpushされる


    let s1 = String::from("hello");
    let s2 = s1;

    これがやってること
    s1というメモリ空間
    ptr にポインタがある | → index 0 1 2 3 4 valueを指す h e l l o
    len 5             |=現在使用してるメモリ量
    capacity 5        |=アロケーターから受け取ったメモリの総量

    s2は s1のポインタが指してる同じメモリ空間をpointer=参照する
    勝手におんなじ場所を参照してくれる

    でも、 s1もs2もスコープから外れたら
    同じhelloのメモリ空間に対して2回、dropすることになる
    = これは double free error
    = メモリコラプションや、セキュリティの問題につながる

    なので s1の行が過ぎた時点でscopeが外れるので、s1は効かなくなる　これで大丈夫なんです
    その次の s2　から hello を呼び出すことができる
    =　この機能を move と言います

    let s1 = String::from("hello");
    let s2 = s1;

    println!("{s1}, world!"); // ここでもうs1は効かない

    これとは逆に、全くメモリをdropする例
    let mut s = String::from("hello");
    s = String::from("ahoy");

    println!("{s}, world!")

    // memoryを意図的にcopyするやり方もあるよ
    let s1 = String::from("hello");
    let s2 = s1.clone();

    println!("s1 = {s1}, s2 = {s2}");

    let x = 5; xに5をbindする
    let y = x; xのcopyを作ってyにbindする
    integerはmoveを考える必要ない、どうせメモリ空間が固定だから、変わらないから
    =これをCopyトレイト
    Rustには、スタックに格納される型（整数など）に付与できる特別なアノテーション
    型がCopyトレイトを実装している場合、それを使用する変数は移動せず、単純にコピーされるため、
    別の変数に代入した後も有効なままです。

    Copyとレイトを持つのは単純なもの
    All the integer types, such as u32.
The Boolean type, bool, with values true and false.
All the floating-point types, such as f64.
The character type, char.
Tuples, if they only contain types that also implement Copy. For example, (i32, i32) implements Copy, but (i32, String) does not.
}

関数とオーナーシップ
fn main() {
    let s = String::from("hello");  // s comes into scope

    takes_ownership(s);             // s's value moves into the function...
                                    // ... and so is no longer valid here

    let x = 5;                      // x comes into scope

    makes_copy(x);                  // Because i32 implements the Copy trait,
                                    // x does NOT move into the function,
                                    // so it's okay to use x afterward.

} // Here, x goes out of scope, then s. However, because s's value was moved,
  // nothing special happens.

fn takes_ownership(some_string: String) { // some_string comes into scope
    println!("{some_string}");
} // Here, some_string goes out of scope and `drop` is called. The backing
  // memory is freed.

fn makes_copy(some_integer: i32) { // some_integer comes into scope
    println!("{some_integer}");
} // Here, some_integer goes out of scope. Nothing special happens.



関数では所有権の移転が必要だけど
こんな面倒なことをしなくても
参照 `referance`　を使えばいけるよ