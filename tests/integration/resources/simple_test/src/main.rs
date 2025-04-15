// Copyright (C) <2024>  INVAP S.E.
// SPDX-License-Identifier: AGPL-3.0-or-later
// Simple hello world used to test program execution

use std::{thread::sleep, time::Duration};

fn component_func(x: i32, y: i32) {
    println!("{}", x + y);
}

fn main() {
    let mut x = 1;
    let mut y = 1;
    println!("Starting loop.");
    for _i in 0..10 {
        x *= 2;
        println!("Value of x: {}", x);
        y *= 3;
        println!("Value of y: {}", y);
        sleep(Duration::from_secs(2));
        component(x, y);
    }
    println!("Finishing loop.");
}