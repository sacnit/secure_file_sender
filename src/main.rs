use crossterm::event::{self, Event};
use crossterm::terminal::{size as terminal_size};
use ratatui::{layout::{Alignment, Constraint, Direction, Layout, Rect}, text::{Line, Text}, widgets::{Block, BorderType, Borders, Paragraph}, Frame};

fn main() {
    let mut terminal = ratatui::init();
    loop {
        terminal.draw(|frame| {
            // Check terminal size
            let (width, height) = terminal_size().expect("Failed to get terminal size");
            if width < 79 || height < 23 {
                // Display a warning if the terminal is too small
                let warning = Paragraph::new(format!("Terminal size too small. ({},{})", width, height))
                    .block(Block::default().borders(Borders::ALL).title("Warning"))
                    .alignment(Alignment::Center);
                frame.render_widget(warning, frame.area());
            } else {
                // Render the main menu if the terminal size is sufficient
                menu_main(frame);
            }
        }).expect("failed to draw frame");

        if matches!(crossterm::event::read().expect("failed to read event"), crossterm::event::Event::Key(_)) {
            break;
        }
    }
    ratatui::restore();
}

fn menu_main(frame: &mut Frame) {
    // Example data
    let ultrapeer = "Ultrapeer Name".to_string();
    let recipient = "Recipient Name".to_string();
    let controls = "Press Q to Quit".to_string();
    let contacts = vec!["Contact 1".to_string(), "Contact 2".to_string(), "Contact 3".to_string()];
    let messages = vec!["Message 1".to_string(), "Message 2".to_string(), "Message 3".to_string()];

    // Outer layout: Top, Main, and Bottom sections
    let outer_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints(vec![
            Constraint::Length(3),
            Constraint::Min(0),
            Constraint::Length(3),
        ])
        .split(frame.area());

    // Top section
    let top_layout = Layout::default()
        .direction(Direction::Horizontal)
        .constraints(vec![
            Constraint::Percentage(30),
            Constraint::Percentage(70),
        ])
        .split(outer_layout[0]);

    // Main section
    let main_layout = Layout::default()
        .direction(Direction::Horizontal)
        .constraints(vec![
            Constraint::Percentage(30),
            Constraint::Percentage(70),
        ])
        .split(outer_layout[1]);

    // Render top_left
    let top_left = Paragraph::new(ultrapeer)
        .block(Block::default().borders(Borders::ALL).title("Ultrapeer"));
    frame.render_widget(top_left, top_layout[0]);

    // Render top_right
    let top_right = Paragraph::new(recipient)
        .block(Block::default().borders(Borders::ALL).title("Recipient"));
    frame.render_widget(top_right, top_layout[1]);

    // Render main_left
    let contact_items: Vec<_> = contacts
        .iter()
        .map(|c| ratatui::widgets::ListItem::new(c.clone()))
        .collect();
    let main_left = ratatui::widgets::List::new(contact_items)
        .block(Block::default().borders(Borders::ALL).title("Contacts"));
    frame.render_widget(main_left, main_layout[0]);

    // Render main_right
    let message_items: Vec<_> = messages
        .iter()
        .map(|m| ratatui::widgets::ListItem::new(m.clone()))
        .collect();
    let main_right = ratatui::widgets::List::new(message_items)
        .block(Block::default().borders(Borders::ALL).title("Messages"));
    frame.render_widget(main_right, main_layout[1]);

    // Render bottom
    let bottom = Paragraph::new(controls)
        .block(Block::default().borders(Borders::ALL).title("Controls"));
    frame.render_widget(bottom, outer_layout[2]);
}