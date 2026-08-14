

struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

// 構造体は、他の何かが所有するデータへの参照を格納することもできますが、
// そのためには、第 10 章で説明する Rust の機能であるライフタイムを使用する必要があります。
// ライフタイムは、構造体によって参照されるデータが、構造体が存在する限り有効であることを保証します。
// src/main.rs でライフタイムを指定せずに構造体に参照を格納しようとした場合、
// 次のようになりますが、これは機能しません。
struct User {
    active: bool,
    username: &str,
    email: &str,
    sign_in_count: u64,
}

struct Color(i32, i32, i32);
struct Point(i32, i32, i32);
fn main() {
    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);
}


fn main() {
    let user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("some@example.com"),
        sign_in_count: 1,
    };
    // emailの値を更新
    user1.email = String::from("another@example.com");

    // 新しいUserを作っているので、user1は残っているよ
    let user2 = User {
        email: String::from("another@example.com"),
        ..user1
    }
}

// Structの内容を変化させて新しいStructを返す
fn build_user(email: String, username: String) -> User {
    User {
        active: true,
        // username: username,
        username,
        // email: email,
        email,
        sign_in_count: 1,
    }
}
