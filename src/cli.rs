pub mod cli {
    use std::collections::HashMap;
    
    extern crate termsize;

#[derive(Debug, PartialEq, Eq, Hash)]
struct BoxCharacterKey {
    up: u8,
    down: u8,
    left: u8,
    right: u8,
    dashes: u8,
    special: bool,
}

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

pub fn select_box_character(directions: &[u8], dashes: u8, special: bool) -> char {
    let map = create_box_character_map();
    let key = BoxCharacterKey {
        up: directions[0],
        down: directions[1],
        left: directions[2],
        right: directions[3],
        dashes,
        special,
    };

    *map.get(&key).unwrap_or(&' ')
}

}