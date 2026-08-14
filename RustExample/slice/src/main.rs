fn first_word(s: &String) -> &str {
    // バイト列に変換
    let bytes = s.as_bytes();

    // enumerate()はtapleで返す
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            // return i; スペースがある位置を返す
            return &s[0..i]; // sliceを参照し
        }
    }
    &s[..]
}

fn main() {
    let my_string = String::from("hello world");

    let word = first_word(&my_string[0..6]);
    let word = first_word(&my_string[..]);

    let word = first_word(&my_string);


    let my_string_literal = "hello world";
    let word = first_word(&my_string_literal[0..6]);
    let word = first_word(&my_string_literal[..]);

    let word = first_word(my_string_literal);
}



// fn main() {
//     let mut s = String::from("hello world");

//     // これだと wordに入った5と s は両立するけど、sは値が変わるかもしれない
//     // なので　 Sliceがあるよ
//     let word = first_word(&s);
//     s.clear(); //ここで不変参照がディアクティブになる
//     println!("the first word is: {word}");
// }





// let s = String::from("hello world");


// let len = s.len();

// let hello = &s[0..5]; // こうやってスライスして、indexの場所を参照`reference`できるよ
// let slice = &s[..5] // こう書いてもいい
// let world = &s[6..11]; // index6番目から6+5で 11番目

// let slice = &s[3..len];
// let slice = &s[3..];

// let slice = &s[0..len];
// let slice = &s[..];