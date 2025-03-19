pub mod event_handler {
    // mvp - Mutex Value Pair is just a struct to reduce number of variables passed through to handle_events
    pub struct MVP {
        keep_running: bool,
        keep_running_mutex: bool,
        redraw_ui: bool,
        redraw_ui_mutex: bool,
        state: i32,
        state_mutex: bool
    }

    impl MVP {
        pub fn new() -> Self {
            MVP { keep_running: true, keep_running_mutex: true, redraw_ui: true, redraw_ui_mutex: true, state: 0, state_mutex: true }
        }
        pub fn get_running(&mut self) -> i32 {
            if self.keep_running_mutex {
                self.keep_running_mutex = false;
                let temp = self.keep_running;
                self.keep_running_mutex = true;
                if temp {return 1;} else {return 0;}
            }
            else {
                return 3;
            }
        }
        pub fn _stop_running(&mut self) -> bool{
            if self.keep_running_mutex {
                self.keep_running_mutex = false;
                self.keep_running = false;
                self.keep_running_mutex = true;
                return true;
            }
            return false;
        }
        pub fn _change_state(&mut self, new_state: i32) -> bool{
            if self.state_mutex {
                self.state_mutex = false;
                self.state = new_state;
                self.state_mutex = true;
                return true;
            }
            return false;
        }
        pub fn toggle_redraw(&mut self) -> bool {
            if self.redraw_ui_mutex {
                self.redraw_ui_mutex = false;
                self.redraw_ui ^= true;
                self.redraw_ui_mutex = true;
            }
            return false;
        }
        pub fn get_redraw(&mut self) -> bool {
            if self.redraw_ui_mutex {
                self.redraw_ui_mutex = false;
                let temp = self.redraw_ui;
                self.redraw_ui_mutex = true;
                return temp;
            }
            return false;
        }
        pub fn get_state(&mut self) -> i32 {
            if self.state_mutex {
                self.state_mutex = false;
                let temp = self.state;
                self.state_mutex = true;
                return temp;
            }
            return 99;
        }
    }
}