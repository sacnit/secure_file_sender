use std::{io::Write, process::exit, sync::{Arc, Mutex}};
//use libp2p;
use cli::cli::*;
use event_handler::event_handler::{event_loop, EventFlags};
use crossterm::{cursor::{Hide, Show}, execute, terminal::{Clear, ClearType}};
use tokio::task;
use ctrlc::set_handler;

mod event_handler;
mod cli;

const SINGLE: u8 = 1;
const DOUBLE: u8 = 2;
const BOLD: u8 = 3;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Handles CTRL + C
    set_handler(move || {
        execute!(std::io::stdout(), Clear(ClearType::Purge)).unwrap();
        execute!(std::io::stdout(), Clear(ClearType::All)).unwrap();
        execute!(std::io::stdout(), Show).unwrap();
        exit(0);
    })?;
    let flags: Arc<Mutex<EventFlags>> = Arc::new(Mutex::new(EventFlags::new()));
    flags.lock().unwrap().set_resize();
    execute!(std::io::stdout(), Hide).unwrap(); // Not supported by all terminals dipshit

    // Spawn the event loop as a separate task
    let mut flags_clone = Arc::clone(&flags); // 分身の術 saving my ass
    let _event_handler = task::spawn(async move {
        event_loop(&mut flags_clone).await;
    });

    loop {
        let terminal_resize = flags.lock().unwrap().get_resize();
        if terminal_resize {
            let mut terminal = initialize_terminal();
            let columns = terminal.width;
            let rows = terminal.height;
            let screen = flags.lock().unwrap().get_screen();
            // Main Screen
            if screen == 0{
                draw_box(&mut terminal, 0, columns, 0, rows, DOUBLE);
                draw_line(&mut terminal, 0, columns, rows - 3, rows - 3, SINGLE);  
            }
            // Help Screen
            if screen == 1{
                draw_box(&mut terminal, 0, columns, 0, rows, DOUBLE);
                draw_line(&mut terminal, 0, columns, rows - 3, rows - 3, SINGLE);  
            }
            // Contacts Screen
            if screen == 2{
                draw_box(&mut terminal, 0, columns, 0, rows, DOUBLE);
                draw_line(&mut terminal, 0, columns, rows - 3, rows - 3, SINGLE);  
            }
            flags.lock().unwrap().reset_resize();
            print!("");      
        }
    }

    //Ok(()) Its not Ok apparently
}