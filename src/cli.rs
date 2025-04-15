pub mod cli {
    use std::{collections::HashMap, io::{stdout, Write}};
    extern crate termsize;
    use crossterm::{cursor, execute, terminal::{Clear, ClearType}};
    
/// structure for defining a box character
/// - up, down, left, right: 0 = single, 1 = double, 3 = bold
/// - dashes: 0 = none, 2 = single, 3 = double, 4 = triple
/// - special: true = special characters, false = regular characters
#[derive(Debug, PartialEq, Eq, Hash, Clone)]
pub struct BoxCharacterKey {
    pub up: u8,
    pub down: u8,
    pub left: u8,
    pub right: u8,
    pub dashes: u8,
    pub special: bool,
}

/// structure for tracking elements on the terminal
pub struct TerminalGrid {
    pub width: u16,
    pub height: u16,
    grid: Vec<Vec<BoxCharacterKey>>
}

/// Creates the hashmap for box characters
fn create_box_character_map() -> HashMap<BoxCharacterKey, char> {
    let mut map = HashMap::new();

    // Add mapping for base case
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 0, right: 0, dashes: 0, special: false }, ' ');

    // Add mappings for mixed characters (bold) ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 3, dashes: 0, special: false }, '╼');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 1, dashes: 0, special: false }, '╾');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 0, right: 0, dashes: 0, special: false }, '╽');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 0, right: 0, dashes: 0, special: false }, '╿');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 0, right: 3, dashes: 0, special: false }, '┍');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 0, right: 1, dashes: 0, special: false }, '┎');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 3, right: 0, dashes: 0, special: false }, '┑');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 1, right: 0, dashes: 0, special: false }, '┒');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 0, right: 3, dashes: 0, special: false }, '┕');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 0, right: 1, dashes: 0, special: false }, '┖');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 3, right: 0, dashes: 0, special: false }, '┙');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 1, right: 0, dashes: 0, special: false }, '┚');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 3, dashes: 0, special: false }, '┝');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 0, right: 1, dashes: 0, special: false }, '┞');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 0, right: 1, dashes: 0, special: false }, '┟');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 1, dashes: 0, special: false }, '┠');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 0, right: 3, dashes: 0, special: false }, '┡');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 0, right: 3, dashes: 0, special: false }, '┢');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 3, right: 0, dashes: 0, special: false }, '┥');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 1, right: 0, dashes: 0, special: false }, '┦');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 1, right: 0, dashes: 0, special: false }, '┧');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 1, right: 0, dashes: 0, special: false }, '┨');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 3, right: 0, dashes: 0, special: false }, '┩');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 3, right: 0, dashes: 0, special: false }, '┪');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 3, right: 1, dashes: 0, special: false }, '┭');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 1, right: 3, dashes: 0, special: false }, '┮');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 3, right: 3, dashes: 0, special: false }, '┯');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 1, right: 1, dashes: 0, special: false }, '┰');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 3, right: 1, dashes: 0, special: false }, '┱');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 1, right: 3, dashes: 0, special: false }, '┲');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 3, right: 1, dashes: 0, special: false }, '┵');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 1, right: 3, dashes: 0, special: false }, '┶');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 3, right: 3, dashes: 0, special: false }, '┷');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 1, right: 1, dashes: 0, special: false }, '┸');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 3, right: 1, dashes: 0, special: false }, '┹');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 1, right: 3, dashes: 0, special: false }, '┺');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 3, right: 1, dashes: 0, special: false }, '┽');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 1, right: 3, dashes: 0, special: false }, '┾');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 3, right: 3, dashes: 0, special: false }, '┿');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 1, right: 1, dashes: 0, special: false }, '╀');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 1, right: 1, dashes: 0, special: false }, '╁');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 1, right: 1, dashes: 0, special: false }, '╂');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 3, right: 1, dashes: 0, special: false }, '╃');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 1, right: 3, dashes: 0, special: false }, '╄');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 3, right: 1, dashes: 0, special: false }, '╅');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 1, right: 3, dashes: 0, special: false }, '╆');
    map.insert(BoxCharacterKey { up: 3, down: 1, left: 3, right: 3, dashes: 0, special: false }, '╇');
    map.insert(BoxCharacterKey { up: 1, down: 3, left: 3, right: 3, dashes: 0, special: false }, '╈');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 3, right: 1, dashes: 0, special: false }, '╉');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 1, right: 3, dashes: 0, special: false }, '╊');

    // Add mappings for mixed characters (double) ✓
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 0, right: 2, dashes: 0, special: false }, '╒');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 0, right: 1, dashes: 0, special: false }, '╓');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 2, right: 0, dashes: 0, special: false }, '╕');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 1, right: 0, dashes: 0, special: false }, '╖');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 0, right: 2, dashes: 0, special: false }, '╘');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 0, right: 1, dashes: 0, special: false }, '╙');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 2, right: 0, dashes: 0, special: false }, '╛');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 1, right: 0, dashes: 0, special: false }, '╜');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 2, dashes: 0, special: false }, '╞');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 0, right: 1, dashes: 0, special: false }, '╟');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 2, right: 0, dashes: 0, special: false }, '╡');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 1, right: 0, dashes: 0, special: false }, '╢');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 2, right: 2, dashes: 0, special: false }, '╤');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 1, right: 1, dashes: 0, special: false }, '╥');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 2, right: 2, dashes: 0, special: false }, '╧');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 1, right: 1, dashes: 0, special: false }, '╨');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 2, right: 2, dashes: 0, special: false }, '╪');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 1, right: 1, dashes: 0, special: false }, '╫');

    // Add mappings for single characters (bold) ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 3, dashes: 0, special: false }, '━');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 0, dashes: 0, special: false }, '┃');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 0, right: 3, dashes: 0, special: false }, '┏');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 3, right: 0, dashes: 0, special: false }, '┓');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 0, right: 3, dashes: 0, special: false }, '┗');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 3, right: 0, dashes: 0, special: false }, '┛');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 3, dashes: 0, special: false }, '┣');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 3, right: 0, dashes: 0, special: false }, '┫');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 3, right: 3, dashes: 0, special: false }, '┳');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 3, right: 3, dashes: 0, special: false }, '┻');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 3, right: 3, dashes: 0, special: false }, '╋');

    // Add mappings for single characters ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 1, dashes: 0, special: false }, '─');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 0, dashes: 0, special: false }, '│');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 0, right: 1, dashes: 0, special: false }, '┌');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 1, right: 0, dashes: 0, special: false }, '┐');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 0, right: 1, dashes: 0, special: false }, '└');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 1, right: 0, dashes: 0, special: false }, '┘');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 1, dashes: 0, special: false }, '├');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 1, right: 0, dashes: 0, special: false }, '┤');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 1, right: 1, dashes: 0, special: false }, '┬');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 1, right: 1, dashes: 0, special: false }, '┴');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 1, right: 1, dashes: 0, special: false }, '┼');

    // Add mappings for double characters ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 2, right: 2, dashes: 0, special: false }, '═');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 0, right: 0, dashes: 0, special: false }, '║');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 0, right: 2, dashes: 0, special: false }, '╔');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 2, right: 0, dashes: 0, special: false }, '╗');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 0, right: 2, dashes: 0, special: false }, '╚');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 2, right: 0, dashes: 0, special: false }, '╝');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 0, right: 2, dashes: 0, special: false }, '╠');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 2, right: 0, dashes: 0, special: false }, '╣');
    map.insert(BoxCharacterKey { up: 0, down: 2, left: 2, right: 2, dashes: 0, special: false }, '╦');
    map.insert(BoxCharacterKey { up: 2, down: 0, left: 2, right: 2, dashes: 0, special: false }, '╩');
    map.insert(BoxCharacterKey { up: 2, down: 2, left: 2, right: 2, dashes: 0, special: false }, '╬');

    // Add mappings for special characters ✓
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 0, dashes: 0, special: true }, '╱');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 1, dashes: 0, special: true }, '╲');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 1, right: 1, dashes: 0, special: true }, '╳');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 0, right: 1, dashes: 0, special: true }, '╰');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 0, right: 1, dashes: 0, special: true }, '╭');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 1, right: 0, dashes: 0, special: true }, '╮');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 1, right: 0, dashes: 0, special: true }, '╯');

    // Add mappings for dashed characters ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 1, dashes: 2, special: true }, '╌');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 1, dashes: 3, special: true }, '┄');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 1, dashes: 4, special: true }, '┈');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 3, dashes: 2, special: true }, '╍');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 3, dashes: 3, special: true }, '┅');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 3, dashes: 4, special: true }, '┉');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 0, dashes: 2, special: true }, '╎');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 0, dashes: 3, special: true }, '┆');
    map.insert(BoxCharacterKey { up: 1, down: 1, left: 0, right: 0, dashes: 4, special: true }, '┊');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 0, dashes: 2, special: true }, '╏');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 0, dashes: 3, special: true }, '┇');
    map.insert(BoxCharacterKey { up: 3, down: 3, left: 0, right: 0, dashes: 4, special: true }, '┋');

    // Add mappings for partial characters ✓
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 1, right: 0, dashes: 0, special: true }, '╴');
    map.insert(BoxCharacterKey { up: 1, down: 0, left: 0, right: 0, dashes: 0, special: true }, '╵');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 0, right: 1, dashes: 0, special: true }, '╶');
    map.insert(BoxCharacterKey { up: 0, down: 1, left: 0, right: 0, dashes: 0, special: true }, '╷');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 3, right: 0, dashes: 0, special: true }, '╸');
    map.insert(BoxCharacterKey { up: 3, down: 0, left: 0, right: 0, dashes: 0, special: true }, '╹');
    map.insert(BoxCharacterKey { up: 0, down: 0, left: 0, right: 3, dashes: 0, special: true }, '╺');
    map.insert(BoxCharacterKey { up: 0, down: 3, left: 0, right: 0, dashes: 0, special: true }, '╻');
    
    // Return the hashmap
    map
}

/// Selects the corresponding box character based on given keys:
///  - `key_1` takes priority over `key_2` in terms of special property
///  - when bold lines (3) and double (2) are both present, double becomes bold
///  - improper combinations return a space character
pub fn select_box_character(map: &HashMap<BoxCharacterKey, char>, key_1: BoxCharacterKey, key_2: Option<BoxCharacterKey>) -> (char, BoxCharacterKey) {

    let key_2 = key_2.unwrap_or(BoxCharacterKey {
        up: 0,
        down: 0,
        left: 0,
        right: 0,
        dashes: 0,
        special: false,
    });

    let mut combined_key = BoxCharacterKey {
        up: if key_1.up == 3 || key_2.up == 3 { 3 } else { key_1.up.max(key_2.up) },
        down: if key_1.down == 3 || key_2.down == 3 { 3 } else { key_1.down.max(key_2.down) },
        left: if key_1.left == 3 || key_2.left == 3 { 3 } else { key_1.left.max(key_2.left) },
        right: if key_1.right == 3 || key_2.right == 3 { 3 } else { key_1.right.max(key_2.right) },
        dashes: key_1.dashes.max(key_2.dashes),
        special: key_1.special,
    };

    if combined_key.up == 3 || combined_key.down == 3 || combined_key.left == 3 || combined_key.right == 3 {
        if combined_key.up == 2 { combined_key.up = 3; }
        if combined_key.down == 2 { combined_key.down = 3; }
        if combined_key.left == 2 { combined_key.left = 3; }
        if combined_key.right == 2 { combined_key.right = 3; }
    }

    (*map.get(&combined_key).unwrap_or(&' '), combined_key)
}

/// Tests the select_box_character function
/// - prints all possible box characters
/// - prints all possible combinations of box characters
pub fn _test_select_box_character() { // Passes ✓
    let map = create_box_character_map();
    let mut seen: Vec<char> = Vec::new();
    let mut seen_combined: Vec<char> = Vec::new();
    for up in 0..=3 {
        for down in 0..=3 {
            for left in 0..=3 {
                for right in 0..=3 {
                    for dashes in 0..=4 {
                        for special in [false, true] {
                            let key_1 = BoxCharacterKey {
                                up,
                                down,
                                left,
                                right,
                                dashes,
                                special,
                            };
                            let character = select_box_character(&map, key_1, None);
                            if !seen.contains(&character.0){
                                seen.push(character.0);
                            }
                        }
                    }
                }
            }
        }
    }
    println!("{:?}{}", seen, seen.len());
    for up in 0..=3 {
        for down in 0..=3 {
            for left in 0..=3 {
                for right in 0..=3 {
                    for dashes in 0..=4 {
                        for special in [false, true] {
                            let key_1 = BoxCharacterKey {
                                up,
                                down,
                                left,
                                right,
                                dashes,
                                special,
                            };
                            for up_2 in 0..=3 {
                                for down_2 in 0..=3 {
                                    for left_2 in 0..=3 {
                                        for right_2 in 0..=3 {
                                            for dashes_2 in 0..=4 {
                                                for special_2 in [false, true] {
                                                    let key_2 = BoxCharacterKey {
                                                        up: up_2,
                                                        down: down_2,
                                                        left: left_2,
                                                        right: right_2,
                                                        dashes: dashes_2,
                                                        special: special_2,
                                                    };
                                                    let character = select_box_character(&map, key_1.clone(), Some(key_2));
                                                    if !seen_combined.contains(&character.0){
                                                        seen_combined.push(character.0);
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    println!("{:?}{}", seen_combined, seen_combined.len());
}

/// Draw box
pub fn draw_box(terminal: &mut TerminalGrid, column_start: u16, column_end: u16, row_start: u16, row_end: u16, style: u8) {
    let map = create_box_character_map();
    for row in row_start..row_end {
        for column in column_start..column_end {
            let mut key_1 = BoxCharacterKey {
                up: 0,
                down: 0,
                left: 0,
                right: 0,
                dashes: 0,
                special: false,
            };
            if row == row_start && column == column_start {
                key_1.right = style;
                key_1.down = style;
            }
            else if row == row_start && column == column_end - 1 {
                key_1.left = style;
                key_1.down = style;
            }
            else if row == row_start {
                key_1.left = style;
                key_1.right = style;
            }
            else if row == row_end - 1 && column == column_start {
                key_1.right = style;
                key_1.up = style;
            }
            else if row == row_end - 1 && column == column_end - 1 {
                key_1.left = style;
                key_1.up = style;
            }
            else if row == row_end - 1 {
                key_1.left = style;
                key_1.right = style;
            }
            else if column == column_start || column == column_end - 1 {
                key_1.up = style;
                key_1.down = style;
            }
            let character = select_box_character(&map, key_1, Some(terminal.grid[row as usize][column as usize].clone()));
            execute!(std::io::stdout(), cursor::MoveTo(column, row)).unwrap();
            print!("{}", character.0);
            terminal.grid[row as usize][column as usize] = character.1;
        }
    }
    stdout().flush().expect("Failed to flush stdout");
}

/// Draw line
pub fn draw_line(terminal: &mut TerminalGrid, column_start: u16, column_end: u16, row_start: u16, row_end: u16, style: u8) {
    let map = create_box_character_map();
    // Vertical
    if column_start == column_end {
        for row in row_start..row_end {
            let mut key_1 = BoxCharacterKey {
                up: style,
                down: style,
                left: 0,
                right: 0,
                dashes: 0,
                special: false,
            };
            if row == row_start {
                key_1.up = 0;
            }
            else if row == row_end - 1 {
                key_1.down = 0;
            }
            let key_2 = Some(terminal.grid[row as usize][column_start as usize].clone());
            let character = select_box_character(&map, key_1, key_2);
            execute!(std::io::stdout(), cursor::MoveTo(column_start, row)).unwrap();
            print!("{}", character.0);
            terminal.grid[row as usize][column_start as usize] = character.1;
        }
    }
    // Horizontal
    else if row_start == row_end {
        for column in column_start..column_end {
            let mut key_1 = BoxCharacterKey {
                up: 0,
                down: 0,
                left: style,
                right: style,
                dashes: 0,
                special: false,
            };
            if column == column_start {
                key_1.left = 0;
            }
            else if column == column_end - 1 {
                key_1.right = 0;
            }
            let key_2 = Some(terminal.grid[row_start as usize][column as usize].clone());
            let character = select_box_character(&map, key_1, key_2);
            execute!(std::io::stdout(), cursor::MoveTo(column, row_start)).unwrap();
            print!("{}", character.0);
            terminal.grid[row_start as usize][column as usize] = character.1;
        }
    }
    stdout().flush().expect("Failed to flush stdout");
}

pub fn draw_text(_terminal: &mut TerminalGrid, column_start: u16, column_end: u16, row_start: u16, row_end: u16, text: &str) {
    let text_length = text.len() as u16;
    let text_segments = text.split(' ');
    let realestate_row = row_end - row_start;
    let realestate_column = column_end - column_start;

    execute!(std::io::stdout(), cursor::MoveTo(column_start, row_start)).unwrap();

    // If the text will fit fine
    if text_length < realestate_column {
        print!("{}", text);
    }
    // If the text will not fit on one row...
    else {
        let mut column_count = 0;
        let mut row_count = 0;
        for segment in text_segments {
            let segment_len = segment.len() + 1;
            if column_count + segment_len > realestate_column.into() {
                // Progress to next row
                column_count = 0;
                row_count += 1;
                execute!(std::io::stdout(), cursor::MoveTo(column_start, row_start + row_count)).unwrap();
            }
            if row_count.eq(&realestate_row) { // Using eq for shits n giggles
                // We are out of rows
                return;
            }
            else {
                print!("{} ", segment);
                column_count += segment_len;
            }
        }        
    }
    stdout().flush().expect("Failed to flush stdout");
}

/// Initializes terminal
pub fn initialize_terminal() -> TerminalGrid {
    execute!(std::io::stdout(), Clear(ClearType::Purge)).unwrap(); // Real nice effort chucklenuts now the screen looks fucky

    let dimensions = termsize::get().unwrap();

    let terminal = TerminalGrid {
        width: dimensions.cols,
        height: dimensions.rows,
        grid: vec![vec![BoxCharacterKey { up: 0, down: 0, left: 0, right: 0, dashes: 0, special: false }; dimensions.cols.into()]; dimensions.rows.into()]
    };
    return terminal
}

}

pub mod cli_dynamic {
    use std::io::{stdout, Write};

    use crossterm::{cursor, execute};

    use crate::BOLD;

    use super::cli::{self, draw_line, draw_text};

    /// Draws as much of the chat in `content` as can fit, deriving whether it's sent or recieved from message prefix
    pub fn render_chat(_terminal: &mut cli::TerminalGrid, column_start: u16, column_end: u16, row_start: u16, row_end: u16, content: Vec<&str>, _rendered: (u16, u16)) {
        let realestate_row = row_end - row_start;
        let realestate_column = column_end - column_start;

        let mut messages: Vec<u16> = vec!();
        for message in content.iter() {
            let mut rows = 1;
            let mut current_row_length = 0;
            for word in message.split_whitespace() {
                let word_length = word.len() as u16 + 1; // Add 1 for the space
                if current_row_length + word_length > realestate_column {
                    rows += 1;
                    current_row_length = word_length;
                } else {
                    current_row_length += word_length;
                }
            }
            messages.push(rows);
        }

        let mut onscreen_messages_count = 0;
        let mut used_rows = 0;
        for &message_rows in messages.iter().rev() {
            if used_rows + message_rows + 1 > realestate_row { // +1 for the separator line
                break;
            }
            used_rows += message_rows + 1;
            onscreen_messages_count += 1;
        }

        let mut current_row = row_end - used_rows;
        for message_index in content.len() - onscreen_messages_count..content.len() {
            let message = content[message_index];
            let message_rows = messages[message_index];
            draw_text(_terminal, column_start, column_end, current_row, current_row + message_rows, message);
            current_row += message_rows;
            draw_line(_terminal, column_start, column_end, current_row, current_row, BOLD);
            let label = if message.starts_with("\x00") { "Sent" } else { "Received" };
            draw_text(_terminal, column_start, column_end, current_row, current_row + 1, label);
            current_row += 1; // Move to the next row after the label
        }
    }

    /// Draws as much of the contacts as can fit
    pub fn render_contacts(_terminal: &mut cli::TerminalGrid, column_start: u16, column_end: u16, row_start: u16, row_end: u16, content: &Vec<&str>, _rendered: (u16, u16)) {
        // Do shit n render the contacts list
        let realestate_row = row_end - row_start;
        let realestate_column = column_end - column_start;

        match _rendered.0 {
            1 => {
                let mut contact_number = 0;
                let mut column = column_start;
                let mut max_column = 0;
                for contact in content.iter() {
                    execute!(std::io::stdout(), cursor::MoveTo(column, row_start+contact_number)).unwrap();
                    let contact_length = contact.len();
                    if contact_length >= realestate_column.into() {
                        print!("{}. {}…", (contact_number + 1 + max_column), &contact[..(realestate_column as usize - 4)]);
                    } else {
                        print!("{}. {}", (contact_number + 1 + max_column), contact);
                    }
                    contact_number += 1;
                    if contact_number > realestate_row {
                        if max_column == 0 {
                            max_column = contact_number;
                        }
                        else {
                            print!("…");
                        }
                        column = _rendered.1 + 1;
                        contact_number = 0;
                    }
                } 
            }
            _=> {
                let mut contact_number = 0;
                for contact in content.iter() {
                    execute!(std::io::stdout(), cursor::MoveTo(column_start, row_start+contact_number)).unwrap();
                    if contact_number == realestate_row {
                        print!("…");
                        break;
                    }
                    let contact_length = contact.len();
                    if contact_length >= realestate_column.into() {
                        print!("{}. {}…", (contact_number + 1), &contact[..(realestate_column as usize - 4)]);
                    } else {
                        print!("{}. {}", (contact_number + 1), contact);
                    }
                    contact_number += 1;
                }                
            }
        }


    }

    /// Draws as much as the hostname as will fit
    pub fn render_host(_terminal: &mut cli::TerminalGrid, column_start: u16, column_end: u16, row_start: u16, _row_end: u16, content: Vec<&str>) {
        // Do shit n render the recipient
        let realestate_column = column_end - column_start;
        let content_length = content[0].len();

        execute!(std::io::stdout(), cursor::MoveTo(column_start, row_start)).unwrap(); 

        if content_length >= realestate_column.into() {
            print!("{}…", &content[0][..(realestate_column as usize - 2)]);
        }
        else {
            print!("{}", content[0]);
        }

        
        stdout().flush().expect("Failed to flush stdout");
    }
}