fn main() {
    let mut count = 0;
    // シングルクオートでloopを始める
    'counting_up: loop{
        println!("count = {count}");
        let mut remaining = 10;

        loop {
            println!("remaining = {remaining}");
            if remaining == 9 {
                break;
            }
            if count == 2 {
                break 'counting_up;
            }
            remaining -= 1;
        }
        count += 1;
    }
    println!("End count = {count}");
    // let result = loop {
    //     counter += 1;

    //     if counter == 10 {
    //         break counter * 2;
    //     }
    // };

    let mut number = 3;

    while number != 0 {
        println!("{number}!");
        number -= 1;
    }

    // エラーしやすいアプローチ
    let a = [10, 20, 30, 40, 50];
    let mut index = 0;
    while index < 5 {
        println!("the value is: {}", a[index]);
        index += 1;
    }

    // 要素分処理するのでエラーしにくい
    for element in a {
        println!("the value is: {element}");
    }

    // revを使う
    for number in (1..6).rev() {
        println!("{number}!");
    }
    println!("LIFTOFF!!!");
    
}
