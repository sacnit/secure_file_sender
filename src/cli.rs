pub mod cli {
    use std::collections::HashMap;
    
    extern crate termsize;

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
pub fn select_box_character(key_1: BoxCharacterKey, key_2: Option<BoxCharacterKey>) -> char {
    let map = create_box_character_map();

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

    *map.get(&combined_key).unwrap_or(&' ')
}

/// Tests the select_box_character function
/// - prints all possible box characters
/// - prints all possible combinations of box characters
pub fn test_select_box_character() {
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
                            let character = select_box_character(key_1, None);
                            if !seen.contains(&character){
                                seen.push(character);
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
                                                    let character = select_box_character(key_1.clone(), Some(key_2));
                                                    if !seen_combined.contains(&character){
                                                        seen_combined.push(character);
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

}