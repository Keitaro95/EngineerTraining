// 構造体でその機能を使用するには明示的にオプトインする必要があります。
// 構造体定義の直前に外側の属性を追加します。
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    // let width1 = 30;
    // let height1 = 50;
    // let rect1 = (30, 50);
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    
    println!(
        "The area of the rectangle is {} square  pixels.",
        area(&rect1)
    );
    println!("rect1 is {rect1:#?}");

    let scale = 2;
    let rect1 = Rectangle {
        width: dbg!(30 * scale),
        height: 50,
    };
    dbg!(&rect1);
}

// fn area(dimensions: (u32, u32)) -> u32 {
//     dimensions.0 * dimensions.1
// }

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}