pub mod screens {
    use array2d::Array2D;

    use crate::cli::cli::*;

    pub fn display_main_menu(grid: &mut Array2D<i32>, grid_entry: &mut Array2D<i32>, _entry_tracker: &mut [String; 20]) -> bool {
        // Clears and initialises the terminal with a border
        clear_screen(grid);

        draw_text_single(start_x, start_y, text, text_colour, text_background, text_style);

        return true;
    }
}