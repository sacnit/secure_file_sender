pub mod event_handler {
    use std::process::exit;
    use std::sync::{Arc, Mutex};
    use crossterm::cursor::Show;
    use crossterm::event::{read, Event, KeyCode};
    use crossterm::terminal::{disable_raw_mode, enable_raw_mode, Clear, ClearType};
    use crossterm::*;

    use signal_hook::consts::signal::SIGWINCH;
    use signal_hook::iterator::Signals;

    
    /// Struct to track event flags
    pub struct EventFlags {
        terminal_resized: bool,
        compiling_message: bool,
        screen: u8, // 0 = Main 1 = Help 2 = Contacts
    }

    impl EventFlags {
        /// Constructor for EventFlags
        pub fn new() -> Self {
            EventFlags {
                terminal_resized: false,
                compiling_message: false,
                screen: 0,
            }
        }
        /// Resets the terminal resize flag
        pub fn reset_resize(&mut self) {
            self.terminal_resized = false;
        }
        /// Sets the terminal resize flag
        pub fn set_resize(&mut self) {
            self.terminal_resized = true;
        }
        /// Returns the terminal resize flag
        pub fn get_resize(&self) -> bool {
            self.terminal_resized
        }
        /// Sets and resets the screen flag
        /// 0 = Main screen 1 = Help screen 2 = Contacts
        pub fn change_screen(&mut self, screen: u8) {
            if self.screen > 0 {
                self.screen = 0;
            }
            else {
               self.screen = screen; 
            }
        }
        /// Returns the screen flag
        /// 0 = Main screen 1 = Help screen 2 = Contacts
        pub fn get_screen(&self) -> u8 {
            self.screen
        }
        /// Sets and resets the screen flag
        /// false = not compiling true = compiling message
        pub fn set_compiling_message(&mut self) {
            match self.compiling_message {
                true => {self.compiling_message = false},
                _ => {self.compiling_message = true}
            }
            self.terminal_resized = true;
        }
        /// Returns the compiling messages flag
        /// false = not compiling true = compiling message
        pub fn get_compiling_message(&self) -> bool{
            self.compiling_message
        }
    }

    pub struct InputStorage {
        input: String,
        changed: bool,
    }

    impl InputStorage {
        /// constructor
        pub fn new() -> Self {
            InputStorage { 
                input: String::new(), 
                changed: false,
            }
        }

        /// For resetting the input string
        pub fn reset_input(&mut self) {
            self.input.clear();
            self.changed = false;
        }

        /// For pushing a character to the input string
        pub fn push_input(&mut self, input: char) {
            self.input.push(input);
            self.changed = true;
        }

        /// Returns the input fields current value
        pub fn get_input(&mut self) -> String {
            self.changed = false;
            self.input.clone()
        }

        /// Returns if the input has changed since last fetched
        pub fn check_input(&self) -> bool {
            self.changed
        }
    }

    /// Event loop for handling signals
    pub async fn event_loop(flags: &mut Arc<Mutex<EventFlags>>) {
        let mut signals = Signals::new(&[SIGWINCH]).unwrap();
        for signal in signals.forever() {
            if signal == SIGWINCH {
                flags.lock().unwrap().set_resize();
            }
        }
    }

    pub async fn input_loop(flags: &mut Arc<Mutex<EventFlags>>, input_field: &mut Arc<Mutex<InputStorage>>) {
        enable_raw_mode().expect("Unable to enable raw mode");

        loop {
            let current_screen = Arc::clone(&flags).lock().unwrap().get_screen();
            match read().expect("Unable to take input") {
                Event::Key(key_event) => {
                    match key_event.code {
                        KeyCode::Char(c) => {
                            {} // For when input can be taken it needs to be taken (no shit)
                            if flags.lock().unwrap().get_compiling_message() {
                                input_field.lock().unwrap().push_input(c);
                            }
                        }
                        KeyCode::F(1) => { // From Main > Help, from All > Main
                            // Get outta dodge if need be
                            flags.lock().unwrap().change_screen(1);
                        }
                        KeyCode::F(2) => { // Main > Contacts, Help - Set Ultrapeer, Contacts - Select Contact
                            match current_screen {
                                0 => flags.lock().unwrap().change_screen(2), // Go to contacts
                                1 => {}, // Set ultrapeer
                                2 => {}, // Select contact
                                _ => flags.lock().unwrap().change_screen(0)
                            }
                        }
                        KeyCode::F(3) => {
                            match current_screen {
                                0 => flags.lock().unwrap().set_compiling_message(), // Compose message
                                1 => {}, // Nothing
                                2 => {}, // Add contact
                                _ => flags.lock().unwrap().change_screen(0)
                            }
                        }
                        KeyCode::F(4) => {
                            match current_screen {
                                0 => {}, // Attach file
                                1 => {}, // Nothing
                                2 => {}, // Remove Contact
                                _ => flags.lock().unwrap().change_screen(0)
                            }
                        }
                        KeyCode::F(5) => {
                            match current_screen {
                                0 => {}, // Send Message
                                1 => {}, // Nothing
                                2 => {}, // Nothing
                                _ => flags.lock().unwrap().change_screen(0)
                            }
                        }
                        KeyCode::F(6) => { // Get outta dodge if need be
                            execute!(std::io::stdout(), Clear(ClearType::Purge)).unwrap();
                            execute!(std::io::stdout(), Clear(ClearType::All)).unwrap();
                            execute!(std::io::stdout(), Show).unwrap();
                            disable_raw_mode().expect("Unable to enable raw mode");
                            exit(0);
                        }
                        _ => {}
                    }
                }
                _ => {}
            }
        }
    }
}