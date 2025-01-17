// use native_tls::TlsConnector;
// use std::io::{Read, Write};
// use std::net::TcpStream;
use std::env;

fn parse_arguments(arguments: Vec<String>) -> bool {
    let mut formatted_arguments: Vec<String> = Vec::new();
    for argument in 1..arguments.len() {
        formatted_arguments.push(arguments[argument].clone());
    }
    dbg!(formatted_arguments);
    return true
}

fn main() {
    let arguments: Vec<String> = env::args().collect();
    parse_arguments(arguments);
    println!("Hello, world!");
}
