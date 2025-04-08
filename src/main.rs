use std::{ fmt::format, io::Write, process::exit, sync::{Arc, Mutex}};
//use libp2p;
use cli::{cli::*, cli_dynamic::*};
use event_handler::event_handler::{event_loop, EventFlags};
use crossterm::{cursor::{Hide, Show}, execute, terminal::{Clear, ClearType}};
use libp2p::futures::stream::Next;
use tokio::task;
use ctrlc::set_handler;

mod event_handler;
mod cli;

const SINGLE: u8 = 1;
const DOUBLE: u8 = 2;
const BOLD: u8 = 3;
const MINCOL: u16 = 80;
const MINROW: u16 = 24;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Example values
    let ultrapeer = vec!["thinkfortwice.1337.cx"]; // Example ultrapeer address
    let contacts = vec![
        "123.456.789.0", "987.654.321.0", "321.654.987.0", "400.400.400.400",
        "192.168.0.1", "10.0.0.1", "172.16.0.1", "8.8.8.8", "8.8.4.4",
        "1.1.1.1", "1.0.0.1", "203.0.113.1", "198.51.100.1", "192.0.2.1",
        "185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153",
        "104.244.42.1", "104.244.43.1", "151.101.1.69", "151.101.65.69",
        "151.101.129.69", "151.101.193.69", "140.82.112.3", "140.82.113.3",
        "140.82.114.3", "140.82.115.3", "192.30.255.112", "192.30.255.113",
        "192.30.255.114", "192.30.255.115", "192.30.255.116", "192.30.255.117",
        "192.30.255.118", "192.30.255.119", "192.30.255.120", "192.30.255.121",
        "192.30.255.122", "192.30.255.123", "192.30.255.124"
    ]; // Just having the IP address may be fine as the Ultrapeer would ideally be queried
    let recipient = vec![1]; // Thinking about having the index stored and then translating to current recipient
    let messages = vec![
        "\x00Hello!", 
        "\x01Hi there! How are you doing today?", 
        "\x00I'm doing well, thanks for asking. How about you?", 
        "\x01Pretty good, just working on some projects.", 
        "\x00That's great to hear. What kind of projects are you working on?", 
        "\x01Oh, just some coding projects. Trying to improve my skills.", 
        "\x00Nice! Coding can be really rewarding.", 
        "\x01Absolutely. What about you? What have you been up to?", 
        "\x00Not much, just testing some terminal rendering logic.", 
        "\x01That sounds interesting. Is it for a specific application?", 
        "\x00Yes, it's for a messaging application I'm working on. It's been a fun challenge to design the interface and handle the networking aspects.", 
        "\x01Cool! Messaging apps are always fun to build. They really help you understand how communication protocols work.", 
        "\x00Indeed. It's a good way to learn about networking and UI. Plus, it's rewarding to see it all come together.", 
        "\x01For sure. Are you using any specific libraries or frameworks for the project?", 
        "\x00Yes, I'm using libp2p for networking and crossterm for terminal UI. Both have been great, though they come with their own learning curves.", 
        "\x01Great choices! libp2p is powerful for peer-to-peer communication, and crossterm is excellent for terminal-based applications.", 
        "\x00Exactly. It's been a learning curve, but I'm getting there. The documentation and examples have been really helpful.", 
        "\x01That's the spirit! Keep at it. The more you work on it, the more you'll learn and improve.", 
        "\x00Thanks! What kind of coding projects are you working on these days? Anything exciting?", 
        "\x01I'm building a small game in Rust. It's a simple text-based adventure with branching storylines and some basic mechanics.", 
        "\x00That sounds awesome! Text-based games are so nostalgic. They remind me of the early days of gaming.", 
        "\x01They really are. It's been fun designing the story and mechanics. I'm trying to make it engaging and replayable.", 
        "\x00I can imagine. Are you planning to share it once it's done? Maybe put it on GitHub for others to try out?", 
        "\x01Yes, I think I will. Sharing it on GitHub seems like a good idea. It'll be interesting to see how people react to it.", 
        "\x00That's a great idea. I'd love to check it out. Text-based games have a charm that's hard to beat.", 
        "\x01Thanks! I'll let you know when it's ready. It's still a work in progress, but I'm making steady progress.", 
        "\x00Looking forward to it. Good luck with the development! I'm sure it'll turn out great.", 
        "\x01Thanks! And good luck with your messaging app too. It sounds like a really cool project.", 
        "\x00Appreciate it. Let's both keep pushing forward and learning as we go!", 
        "\x01Absolutely. Take care and happy coding!"
    ];

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
            if columns < MINCOL || rows < MINROW {
                execute!(std::io::stdout(), Clear(ClearType::All)).unwrap();
                println!("Terminal size is too small. Minimum size is {}x{}", MINCOL, MINROW);
            }
            else{
                let screen = flags.lock().unwrap().get_screen();
                // Main Screen
                if screen == 0{
                    let contacts_clone = contacts.clone();
                    draw_box(&mut terminal, 0, columns, 0, rows, DOUBLE); // Outside border
                    draw_line(&mut terminal, 0, columns, rows - 3, rows - 3, SINGLE); // Function menu border
                    draw_text(&mut terminal, 1, columns - 1, rows - 2, rows - 2, "F1-Help F2-Contacts F3-Compose Message F4-Attach File F5-Send Message F6-Exit"); // Function menu
                    draw_line(&mut terminal, 0, columns, 2, 2, SINGLE); // Info border
                    draw_line(&mut terminal, (columns / 3).into(), (columns / 3).into(), 0, rows - 2, SINGLE); // Info divider
                    draw_text(&mut terminal, 1, 11, 0, 0, "Ultrapeer:"); // Ultrapeer label
                    render_host(&mut terminal, 11, ((columns / 3) - 1).into(), 1, 1, ultrapeer.clone()); // Ultrapeer
                    draw_text(&mut terminal, ((columns / 3) + 1).into(), ((columns / 3) + 11).into(), 0, 0, "Recipient:"); // Recipient label
                    render_host(&mut terminal, ((columns / 3) + 11).into(), columns - 1, 1, 1, vec![contacts_clone[recipient[0] as usize]]); // Recipient
                    render_contacts(&mut terminal, 1, (columns / 3).into(), 3, rows - 4, &contacts, (0,0));
                    render_chat(&mut terminal, ((columns / 3) + 1).into(), columns - 1, 3, rows - 4, messages.clone(), (0,0));
                    
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
    }

    //Ok(()) Its not Ok apparently
}