// Copyright (C) <2024>  INVAP S.E.
// SPDX-License-Identifier: AGPL-3.0-or-later
// Simple hello world used to test program execution

use std::{thread::sleep, time::Duration};

mod component;
use crate::component::{component};

fn main() {
    let mut x = 1;
    let mut y = 1;
    let mut c = component::new();
    println!("Starting loop.");
    for i in 0..10 {
        x *= 2;  // task_started,loopbody
        println!("Value of x: {}", x);
        y *= 3;
        println!("Value of y: {}", y);
        let mut z = c.component_func(x, y);  // checkpoint_reached,loop_inv_chk - component,component_func - task_finished,loopbody -- main.rs:20:b,component_event,component,component_func,x,y
        println!("{}", z);
        sleep(Duration::from_secs(2));
        println!()  // checkpoint_reached,chk_sleep
    }
    println!("Finishing loop.");
}