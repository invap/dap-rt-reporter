// Copyright (C) <2024>  INVAP S.E.
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Simple program to test basic library functionalities


fn test_function(num: i32) -> i32{
    return num;
}

fn main(){
    //Declaracion de 4 variables
    let mut a;
    let mut b;
    let mut c;
    let mut d;

    //Task started, init
    //Asignacion a las 4 variables
    a = 1;
    b = 2;
    c = 3;
    d = 4;
    a = test(a);

    //Task finished, init
    while d < 10000{
        //Task started, filtering
        while a < 10{
            //Asignaciones a las variables a, b, c
            a += 1;
            b += 2;
            c += 3;
            //Checkpoint reached, filtering_chk
        }
        //Task finished, filtering
        //Task started, conversion
        //Asignacion a d
        d += 2 * (a * b + c);
        //Task finished, conversion
        //Checkpoint reached, display_ok
    }
}