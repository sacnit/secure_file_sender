pub mod event_handler {
    use std::sync::{Arc, Mutex};

    use signal_hook::consts::signal::SIGWINCH;
    use signal_hook::iterator::Signals;

    
    /// Struct to track event flags
    #[derive(Clone)]
    pub struct EventFlags {
        terminal_resized: bool,
    }

    impl EventFlags {
        /// Constructor for EventFlags
        pub fn new() -> Self {
            EventFlags {
                terminal_resized: false,
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
}