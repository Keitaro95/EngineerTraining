fn main() {
    println!("{} days", 31);

    println!("{0}, this is {1}.z¥n {1}, this is {0}", "Alice", "Bob");

    println!("{subject} {verb} {object}",
            object="the lazy dog",
            subject="the quick brown fox",
            verb="jumps over
            ");

    println!("Base 10: {}", 69420);
    println!("Base 2(binary): {:b}", 69420);
    println!("Base octal: {:o}", 69420);
    println!("Base hex: {:x}", 69420);

    // padding 
    println!("{number:0>5}", number=1);
    // println!("{number:0<5}", number=1);

    println!("{number:0<width$}", number=1, width=5);

    println!("My name is {0}, {1} {0}", "Bond", "James");
    
    // println!("This struct `{}` won't print...", Structure(3));

    let number: f64 = 1.0;
    let width: usize = 5;
    println!("{number:>width$}");

    // Pi is roughly 3.142
    let pi = 3.141592;

    println!("Pi is roughly {:.3}", pi);
}