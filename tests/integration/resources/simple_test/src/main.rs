// Simple hello world used to test program execution

use std::{thread::sleep, time::Duration};

fn main() {
    let x = 145;
    println!("{}", x);
    println!("Hello World!");
    println!("Hello World!");
    sleep(Duration::from_secs(2));
    println!("Hello World!");
    let x = 11;
    println!("{}", x);
    println!("Hello World!");
    println!("Hello World!");
}
