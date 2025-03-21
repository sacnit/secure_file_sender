//use libp2p;
use cli::cli::*;

mod cli;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    test_select_box_character();

    Ok(())
}