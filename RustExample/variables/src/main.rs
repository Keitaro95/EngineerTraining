use std::io;

fn main() {
    // let mut x = 5;
    // println!("The value of x is: {x}");
    // x = 6;
    // println!("The value of x is: {x}");

    // const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 *3;


    // let x = 5; // shadowed variable 影に覆われる変数

    // let x = x + 1;

    // {
    //     let x = x * 2;
    //     println!("The value of x in the inner scope is: {x}");
    // }

    // println!("The value of x is: {x}");

    // // 新しい変数を宣言
    // let spaces = "   ";

    // let spaces = spaces.len();
    
    // let guess: u32 = "42".parse().expect("Not a number!");
    

    // // taple
    // let x: (i32, f64, u8) = (500, 6.4, 1);
    // let five_hundred = x.0;
    // let six_point_four = x.1;
    // let one = x.2;

    // // Array ベクトル型より柔軟性を欠く
    let a = [1, 2, 3, 4, 5];

    println!("Please enter an array index.");

    let mut index = String::new();

    io::stdin()
        .read_line(&mut index)
        .expect("Failed to read line");

    let index: usize = index
        .trim()
        .parse()
        .expect("Index entered was not a number");

    let element = a[index];

    println!("The value of the element at index {index} is: {element}");

    // これで10とか入れると即座にエラーを返す
    // なのでメモリ安全に、処理を停止できる

    // let a: [i32; 5] = [1, 2, 3, 4, 5];

    // let a = [3; 5]

    // これは
    // let a = [3, 3, 3, 3, 3]; 
    // と同じ

    // let a = [1, 2, 3, 4, 5];

    // let first = a[0];
    // let second = a[1];


}
