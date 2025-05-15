// Copyright (C) <2024>  INVAP S.E.
// SPDX-License-Identifier: AGPL-3.0-or-later
// Simple hello world used to test program execution

pub struct Component {
    value: i32,
}

impl Component {
    pub fn new() -> Self {
        Component {
            value: 0,
        }
    }

    pub fn component_func(&mut self, x: i32, y: i32) -> i32 {
        self.value = x + y;
        self.value
    }
}

