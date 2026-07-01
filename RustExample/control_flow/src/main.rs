fn main() {

    let number = 3;

    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }

    let number_2 = 0;

    if number_2 != 0 {
        println!("number was something other than zero");
    } else  {
        println!("number is zero");
    }

    // Rustが最初の真の条件に対してのみブロックを実行し、一度真の条件が見つかると、残りの条件はチェックしない
    let number_3 = 6;
    if number_3 % 4 == 0 {
        println!("number_3 is divisible by 4");
    } else if number_3 % 3 == 0 {
        println!("number_3 is divisible by 3");
    } else if number_3 % 2 == 0 {
        println!("number_3 is divisible by 2");
    } else {
        println!("number is not divisible by 4, 3, or 2");
    }

    let condition = true;
    let number_condition = if condition { 5 } else { 6 };

    println!("The value of number is: {number_condition}")
}

