//use libp2p;
use std::io::stdin;
use array2d::Array2D;
use cli::cli::*;

mod cli;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    print!("{}", select_box_character(&[1,0,0,1], 0, true));

    Ok(())
}