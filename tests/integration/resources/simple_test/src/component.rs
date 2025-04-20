// Copyright (C) <2024>  INVAP S.E.
// SPDX-License-Identifier: AGPL-3.0-or-later
// Simple hello world used to test program execution

pub struct component {
    value: i32,
}

impl component {
    /// Creates a new component with the specified initial value
    pub fn new() -> Self {
        component {
            value: 0,
        }
    }

    pub fn component_func(&mut self, x: i32, y: i32) -> i32 {
        self.value = x + y;
        x + y
    }
}

