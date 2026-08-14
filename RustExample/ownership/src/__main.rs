// 格式ばった書き方
// fn main() {
//     let s1 = String::from("hello");

//     let (s2, len) = caluculate_length(s1);

//     println!("The length of '{s2} is {len}.");
// }

// fn caluculate_length(s: String) -> (String, usize) {
//     let length = s.len();

//     (s, length)
// }


fn main() {
    // s1はptr部分で helloのメモリ空間をpointするよ
    let s1 = String::from("hello");

    // caluculate_length(s)のsは &s1 となっているので、s1を参照するよ
    // このs1は参照しているだけで、所有していないよ。だから、上の s1 の行は dropされないよ
    let len = caluculate_length(&s1); 

    println!("The length of '{s1} is {len}.");
}


// [めっちゃ重要]所有権を持たない関数
// この関数の引数は、そもそも参照を引数で取ると宣言している
// なので所有権を持たないと持たないと宣言している
// だから所有権を返すためにわざとらしく値を返す必要がない
fn caluculate_length(s: &String) -> usize {
    s.len()
} // ここでsはscope外になるけど、sは参照によって入るものだし
// そもそも、sは所有権を持たないので、dropもされない。