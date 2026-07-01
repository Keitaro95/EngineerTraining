// ioを stdライブラリから取り込む
use std::io;
use std::cmp::Ordering;

use rand::Rng;

fn main() {
    println!("Guess the number!");

    // function that gives us the particular random number generator we’re going to use:
    // gen_range(1..=100)で範囲を指定
    let secret_number = rand::thread_rng().gen_range(1..=100);

    println!("The secret number is: {secret_number}");

    loop {
        println!("Please input your guess.");

        let mut guess = String::new();

        // mutableでString型で、空の新しい変数だよ
        // String 型の 空の新しいインスタンス を生成する関連関数(associated function)
        // 関連関数とは、型（この場合は String）に実装されている関数のことです
        // この new 関数は、新しい空の文字列を作成します
        // new 関数は、何らかの新しい値を作成する関数の一般的な名前であるため
        // 多くの型で見つけることができます。
        let mut guess = String::new();

        // user inputを扱う stdin() 
        // モジュールをimport しない場合は std::io::stdin と書いてもいい
        // `read_line` メソッドを呼び出して、ユーザーからの入力を取得
        // &mut guessと書くことで、メモリに何回もコピーしないで参照できる
        // ひとまずは、 &mut guess と書いてmutableにしてね
        io::stdin()
            .read_line(&mut guess) 
            .expect("Failed to read line");

        // こうして guessを別のtypeに変換できる
        // なので guess をいろいろな型に変化して使いまわせる
        // guessに対して trim して 5\　を 5だけにする
        //  parseは stringを別の型に変換する
        // let guess: u32 = guess.trim().parse().expect("Please type a number!");

        // parseはResult型を返し、ResultはOkとErrというバリアントを持つ列挙型
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        println!("You guessed: {guess}");

        // 秘密の数字とuser inputを比べる
        // match のなかに 分岐である arm　を書く
        match guess.cmp(&secret_number) {
            // この中の3つはバリアント
            // 2つの結果を比べた時の結果を表す
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}
