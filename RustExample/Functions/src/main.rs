fn main() {
    println!("Hello, world!");
    another_function(5, 'h');
    let y = {
        let x = 3;
        x + 1 // ここはexpressionの行なのでセミコロンなし。
        // もしセミコロンつけたら statement ということになる
    };

    println!("The value of y is: {y}");

    let x = five(); // 変数を初期化する

    let z =plus_one(10);
    println!("The value of z is: {z}");

    println!("The value of x is: {x}");
}

fn another_function(value: i32, unit_label: char) {
    println!("This is Another function. The measurement is: {value}{unit_label}");
}

fn five() -> i32 {
    5 // この値を返したいのでセミコロンなしのexpression
}

fn plus_one(x: i32) -> i32 {
    x + 1; // ここにセミコロンをつけるとstatementになり()として返ったことになるからエラー
}