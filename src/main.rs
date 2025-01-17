// use native_tls::TlsConnector;
// use std::io::{Read, Write};
// use std::net::TcpStream;
use std::env;

struct Parameters {
    r#type: Option<bool>,
    ultrapeer: Option<String>,
}

// Implement length checks and error handling for missing values
fn parse_arguments(arguments: Vec<String>, parameters: &mut Parameters) {
    for argument_index in 1..arguments.len() {
        let current_argument = arguments[argument_index].clone();
        let current_argument_prefix = &current_argument[0..2];
        if current_argument_prefix == "--" {
            if &current_argument[2..] == "type" {
                parameters.r#type = if arguments[argument_index + 1] == "ultrapeer".to_string() {Some(true)} else {Some(false)};
            }
        }
    }
}

fn main() {
    let mut parameters = Parameters {
        r#type: None,
        ultrapeer: None,
    };
    let arguments: Vec<String> = env::args().collect(); 
    parse_arguments(arguments, &mut parameters);
    println!("Hello, world!");
}
