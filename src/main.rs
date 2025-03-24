use std::sync::{Arc, Mutex};
//use libp2p;
use cli::cli::*;
use event_handler::event_handler::{event_loop, EventFlags};
use crossterm::{cursor::Hide, execute, terminal::EnterAlternateScreen};
use tokio::task;

mod event_handler;
mod cli;

struct Cleanup;

// So the terminal doesnt shit itself
impl Drop for Cleanup {
    fn drop(&mut self) {
        // Since EnterAlternateScreen is called, it needs to be left before the program exits
        execute!(std::io::stdout(), crossterm::terminal::LeaveAlternateScreen).unwrap();
    }
    
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let _cleanup = Cleanup;
    let mut flags: Arc<Mutex<EventFlags>> = Arc::new(Mutex::new(EventFlags::new()));
    execute!(std::io::stdout(), EnterAlternateScreen ).unwrap();
    execute!(std::io::stdout(), Hide).unwrap(); // Not supported by all terminals dipshit

    // Spawn the event loop as a separate task
    let _event_handler = task::spawn(async move {
        event_loop(&mut flags).await;
    });

    loop {
        let terminal_resize = flags.lock().unwrap().get_resize(); // MASSIVE BLEEDING TWAT
        if terminal_resize {
            let terminal = initialize_terminal();
            let columns = terminal.width;
            let rows = terminal.height;
            draw_box(terminal, 0, columns, 0, rows, 2);
            flags.lock().unwrap().reset_resize();      
        }
    }

    //Ok(()) Its not Ok apparently
}