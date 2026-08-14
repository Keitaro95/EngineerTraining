
// 列挙型
enum IpAddrKind {
    V4,
    V6,
}
let four = IpAddrKing::V4;
let six = IpAddrKind::V6;
fn route(ip_kind: IpAddrKind) {}
route(IpAddrKind::V4);
route(IpAddrKind::V6);


enum IpAddr {
    V4(String),
    V6(String),
}
// バリアントに対して直接データ付加する
let home = IpAddr::V4(String::from("127.0.0.1"));
let loopback = ApAddr::V6(String::from("::1"));


// 列挙型のメリット
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}
let home = IpAddr::V4(127, 0, 0, 1);
let loopback = IpAddr::V6(String::from("::1"));


enum Message {
    Quit, // 関連データなし
    Move { x: i32, y: i32 }, // 名前付きフィールドを持つ
    Write(String), // 1このString
    ChangeColor(i32, i32, i32),
}

impl Message {
    fn call(&self) {
        // method
    }
}
let m = Message::Write(String::from("hello"));
m.call();

// これを構造体で書くとめんどい
struct QuitMessage;
struct MoveMessage {
    x: i32,
    y: i32,
}
struct WriteMessage(String);
struct ChangeColorMessage(i32, i32, i32);

Rustには null はないけど、 値が存在するかしないかを表現できる列挙型がある

enum Option<T> {
    None,
    Some(T),
}
let some_number = Some(5);
let some_char = Some('e');
let absent_number: Option<i32> = None;



enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    // coin って値を出す条件分岐
    match coin {
        Coin::Penny => {
            println!("Lucky penny!";)
            1
        }
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}


#[derive(debug)]
enum UsState {
    Alabama,
    Alaska,
    // 
}

enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

fn value_in_cents_each_states(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => {
            println!("State quarter from {state:?}!");
            25
        }
    }
}

Coin::Quarter(UsState::Alaska) 
// と呼び出せる

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None, // 
        Some(i) => Some(i + 1),
    }
}

let five = Some(5); 
let six = plus_one(five); // x = Some(5) → Some(i) に入るので iに5が入る → Some(6) を返す
let none = plus_one(None);


fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        // exhaustiveness = 網羅性：Noneの行がないよ、とエラーを吐いてくれる
        Some(i) => Some(i + 1),
    }
}


## 包括的パターンと _ プレースホルダー


// other＝マッチした値を受け取って使える。包括的パターン。それ以外の値を全部代入できる
let dice_roll = 9;
match dice_roll {
    3 => add_fancy_hat(),
    7 => remove_fancy_hat(),
    // 3,7以外の値を全て入れられる
    other => move_player(other), // otherと書くことで、u8が取りうるすべての値にmatchさせる。
}
fn add_fancy_hat() {}
fn remove_fancy_hat() {}
fn move_player(num_spaces: u8) {}


// _（アンダースコア）マッチするが値は使えない、ただその時起こしたい処理を書く
let dice_rill = 9;
match dice_roll {
    3 => add_fancy_hat(),
    7 => remove_fancy_hat(),
    // 3,7以外の値がきたらこの処理でストップする
    _ => reroll(), // 3,7以外の値でやること
    // _ => (), って書くと何もしないことを表す
}

fn add_fancy_hat() {}
fn remove_fancy_hat() {}
fn reroll() {}


let config_max = Some(3u8);
match config_max {
    Some(max) => println!("The maximum is configured to be {max}"),
    _ => (), // Some関数以外のわざわざこのためだけに プレースホルダを書きたくない
}

let config_max = Some(3u8);
// 最初のパターンをarmとする 
// match文の代わりと考えることができる
if let Some(max) = config_max {
    println!("The maximum is configured to be {max}");
}

let mut count = 0;
match coin {
    Coin::Quarter(state) => println!("State quarter from {state:?}"),
    _ => count += 1,
}
// if let で書くとこうなります
if let Coin::Quarter(state) => coin {
    println!("State quarter from {state:?}!");
} else {
    count += 1;
}


impl UsState {
    fn existed_in(&self, year: u16) -> bool {
        match_self {
            UsState::Alabama => year >= 1819,
            UsState::Alaska => year >= 1959,
        }
    }
}

// 冗長になってします
fn describe_state_quarter(coin: Coin) -> Option<String> {
    if let Coin::Quarter(state) = coin {
        if state.existed_in(1900) {
            Some(format!("{state:?} is pretty old, for America!"))
        } else {
            Some(format!("{state:?} is relatively new."))
        }
    } else {
        None
    }
}

// 書き方②：= が2つ、state が2つ、読みにくい
fn describe_state_quarter(coin: Coin) -> Option<String> {
    // if let を式にできる。
    // Coin:: Quarter(state) 
    let state = if let Coin:: Quarter(state) = coin {
        // UsStateの中身
        state 
    } else {
        return None;
    };
    if state.existed_in(1900) {
        Some(format!("{state:?} is pretty old, for America!"))
    } else {
        Some(format!("{state:?} is relatively new."))
    }
}

// 書き方③は②の読みにくさを解消したもの（let...else）= は1つ、すっきり
fn describe_state_quarter(coin: Coin) -> Option<String> {
    let Coin::Quarter(state) = coin else {
        return None;
    };
    if state.existed_in(1900) {
        Some(format!("{state:?} is pretty old for America!"))
    } else {
        Some(format!("{state:?} is relatively new."))
    }
}