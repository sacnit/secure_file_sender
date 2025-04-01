pub mod event_handler {
    use std::sync::{Arc, Mutex};
    use crossterm::*;

    use signal_hook::consts::signal::SIGWINCH;
    use signal_hook::iterator::Signals;

    
    /// Struct to track event flags
    #[derive(Clone)]
    pub struct EventFlags {
        terminal_resized: bool,
        screen: u8, // 0 = Main 1 = Help 2 = Contacts
    }

    impl EventFlags {
        /// Constructor for EventFlags
        pub fn new() -> Self {
            EventFlags {
                terminal_resized: false,
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
            if screen > 0 {
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

    pub async fn input_loop(flags: &mut Arc<Mutex<EventFlags>>) {
        
    }
}