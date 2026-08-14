fn main() {
    // let s = String::from("hello");

    let mut s = String::from("hello");

    // change(&s);

    // mutable referenceにする
    change(&mut s);
    println!("{s}")

    // 可変参照を2つは持てない：restriction
    let r1 = &mut s; // 棄却されるまで続く
    let r2 = &mut s; // 制約があるので参照できない

    println!("{r1}, {r2}");
    同じデータへの複数の可変参照を同時に禁止する制限により、変更は可能になりますが、
    非常に制御された方法で行われます。ほとんどの言語ではいつでも変更できるため、
    これはRust初心者にとって理解しにくい点です。
    この制限の利点は、Rustがコンパイル時にデータ競合を防止できることです。
    データ競合は競合状態に似ており、次の3つの動作が発生した場合に起こります。

    データレースが起こるパターン
    - 2つ以上のpointerが同じデータを同じタイミングで参照する
    - ポイントの1つがデータを書くために使われている時
    - 同期アクセスtoデータのメカニズムはない

    Rustはデータレースが起こってるコードをコンパイル弾きます

    ## Mutable Referance
    let mut s = String::from("hello");
    // 新しいscopeを作る
    {
        let r1 = &mut s;
    } 
    let r2 = &mut s;


    let mut s = String::from("hello");
    let r1 = &s; //問題なし
    let r2 = &s; //問題なし
    let r3 = &mut s; //mutable referenceは大問題



    let mut s = String::from("hello");
    let r1 = &s; // no problem
    let r2 = &s; // no problem
    println!("{r1} and {r2}");
    // Variables r1 and r2 will not be used after this point.
    // だから mutable referenceが許される

    let r3 = &mut s; // no problem
    println!("{r3}");

}

// fn change(some_string: &String) {
//     some_string.push_str(", world");
// }

// mutable referenceにする
fn change(some_string: &mut String) {
    some_string.push_str(", world");
}