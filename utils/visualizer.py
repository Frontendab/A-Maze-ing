"""Visualizer utility functions for the A-Maze-ing project.
It contains structures that handle the maze visualization using MLX, and
functions to draw and animate the maze generation and path finding algorithms.
It exposes the launch_visualizer function to start the visualizer with the
configuration dictionary.
"""

from enum import Enum
from random import randint
import sys
from typing import Any, Callable, Dict, List, Tuple
from mazegen import Cell
from mlx import Mlx
from mazegen import MazeGenerator
from .font_large import FONT_LARGE
from collections import namedtuple


"""Defining color palette structure as a named tuple."""
Palette = namedtuple(
    'Palette',
    ['bg_color', 'wall_color', 'path_color', 'pattern_color']
)

"""Predefined color palettes"""
COLOR_PALETTES = [
    Palette(0xFF09152B, 0xFFECF9FF, 0xFF00B0FC, 0xFF035CC2),
    Palette(0xFF023047, 0xFF219EBC, 0xFFFFB703, 0xFFFB8500),
    Palette(0xFF401D40, 0xFFA050A0, 0xFF98B840, 0xFFD8C0F8),
    Palette(0xFF1D1D1D, 0xFFCAE9EA, 0xFF208C8C, 0xFF3C4748)
]


class ImgData:
    """
    Structure for image data.

    Attributes:
        img (int | None): Image pointer.
        width (int): Image width.
        height (int): Image height.
        data (memoryview[int]): Image data memoryview.
        sl (int): Size line.
        bpp (int): Bits per pixel.
        iformat (int): Image format.
    """
    def __init__(self) -> None:
        """Image Data constructor.
        """
        self.img: int | None = None
        self.width: int = 0
        self.height: int = 0
        self.data: memoryview[int]
        self.sl: int = 0
        self.bpp: int = 0
        self.iformat: int = 0


class Anim:
    """Structure for animation parameters.

    Attributes:
        steps (Any): Steps generator.
        prev_cell (Tuple[int, int]): Previous cell position in DFS.
        tick (int): Animation tick counter.
        speed (int): Animation speed.
        done (bool): Maze generation animation done flag.
        old_path (list): Old path cells for path finding animation.
        path_done (bool): Path finding animation done flag.
    """
    def __init__(self, steps_generator: Any) -> None:
        """Animation parameters constructor.

        Args:
            steps_generator (Any): Steps generator.
        """
        self.steps: Any = steps_generator
        self.prev_cell: Tuple[int, int]
        self.tick: int = 0
        self.speed: int = 5
        self.done: bool = False
        self.old_path: list = []
        self.path_done: bool = False


class Status(Enum):
    """Enum for visualizer status."""
    INTRO = 1
    RUNNING = 2


class XVar:
    """Structure for visualization global variables.

    Attributes:
        mlx (Mlx): MLX instance.
        mlx_ptr (int): MLX pointer.
        win (int): Main window pointer.
        logo_img (ImgData): Logo image data.
        main_img (ImgData): Main image data.
        hud_img (ImgData): HUD image data.
        screen_w (int): Screen width.
        screen_h (int): Screen height.
        win_w (int): Window width.
        win_h (int): Window height.
        status (Status): Visualizer status.
        gen (MazeGenerator): Maze generator instance.
        algo (str): Current maze generation algorithm.
        anim (Any): Animation instance.
        toggle_path_finding (bool): Path finding visualization toggle flag.
        buttons (List[Button]): List of buttons.
    """
    def __init__(self) -> None:
        self.mlx: Mlx
        self.mlx_ptr: int
        self.win: int
        self.logo_img: ImgData = ImgData()
        self.main_img: ImgData = ImgData()
        self.hud_img: ImgData = ImgData()
        self.screen_w: int = 0
        self.screen_h: int = 0
        self.win_w: int = 0
        self.win_h: int = 0
        self.status: Status = Status.INTRO
        self.gen: MazeGenerator
        self.algo: str = "DFS"
        self.anim: Any = None
        self.toggle_path_finding: bool = True
        self.buttons: List[Button] = []


class RenderingVar:
    """Structure for rendering variables.

    Attributes:
        maze_w (int): Maze area width.
        maze_h (int): Maze area height.
        hud_w (int): HUD area width.
        hud_h (int): HUD area height.
        maze_x (int): Maze area X position.
        maze_y (int): Maze area Y position.
        hud_x (int): HUD area X position.
        hud_y (int): HUD area Y position.
        button_border (int): Button border size.
        bd_thickness (int): Maze wall thickness.
        cell_padding (int): Cell padding size.
        cell_size (int): Cell size.
        palette_idx (int): Current color palette index.
        color_palette (Palette): Current color palette.
    """
    def __init__(self) -> None:
        self.maze_w: int = 0
        self.maze_h: int = 0
        self.hud_w: int = 0
        self.hud_h: int = 0

        self.maze_x: int = 0
        self.maze_y: int = 0
        self.hud_x: int = 0
        self.hud_y: int = 0

        self.button_border: int = 3
        self.bd_thickness: int = 10
        self.cell_padding: int = 4
        self.cell_size: int = 35

        self.palette_idx: int = 0
        self.color_palette: Palette = COLOR_PALETTES[self.palette_idx]


class Button:
    """Structure defining a button.

    Attributes:
        x (int): X position.
        y (int): Y position.
        w (int): Width.
        h (int): Height.
        label (str): Button label.
        color (int): Button color.
        on_click (Any): Button on click callback.
    """
    def __init__(self,
                 x: int, y: int,
                 w: int, h: int,
                 label: str,
                 color: int,
                 on_click: Any
                 ) -> None:
        """Button constructor.

        Args:
            x (int): X position.
            y (int): Y position.
            w (int): Width.
            h (int): Height.
            label (str): Button label.
            color (int): Button color.
            on_click (Any): Button on click callback.
        """
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        self.label: str = label
        self.color: int = color
        self.on_click: Callable[[XVar, RenderingVar], None] = on_click

    def mouse_over(self, mx: int, my: int) -> bool:
        """Checks whether the mouse is over the button or not.

        Args:
            mx (int): Mouse X position.
            my (int): Mouse Y position.

        Returns:
            bool: True if mouse is over the button, False otherwise.
        """
        return (
            self.x <= mx <= self.x + self.w and
            self.y <= my <= self.y + self.h
        )


def init_params(config: Dict[str, Any]) -> tuple[XVar, RenderingVar]:
    """Initializes visualizer global parameters and rendring variables.

    Args:
        config (Dict[str, Any]): Configuration dictionary.

    Raises:
        Exception: When MLX intitialization fails.
        Exception: When window creation fails.

    Returns:
        tuple[XVar, RenderingVar]: Tuple containing XVar and RendringVar
        instances.
    """
    xvar = XVar()
    rvar = RenderingVar()

    try:
        xvar.mlx = Mlx()
    except Exception as e:
        print(f"Error: Can't initialize MLX: {e}", file=sys.stderr)
        sys.exit(1)
    xvar.mlx_ptr = xvar.mlx.mlx_init()
    (
        _,
        xvar.screen_w,
        xvar.screen_h
    ) = xvar.mlx.mlx_get_screen_size(xvar.mlx_ptr)

    try:
        if 'SEED' in config.keys():
            xvar.gen = MazeGenerator(
                config['WIDTH'], config['HEIGHT'],
                config['ENTRY'], config['EXIT'],
                config['OUTPUT_FILE'], config['PERFECT'],
                config['SEED']
                )
        else:
            xvar.gen = MazeGenerator(
                config['WIDTH'], config['HEIGHT'],
                config['ENTRY'], config['EXIT'],
                config['OUTPUT_FILE'],
                config['PERFECT']
                )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    rvar.maze_w = xvar.gen.width * rvar.cell_size + rvar.bd_thickness * 2
    rvar.maze_h = xvar.gen.height * rvar.cell_size + rvar.bd_thickness * 2
    rvar.maze_x = 0
    rvar.maze_y = 0
    rvar.hud_w = 250
    rvar.hud_h = rvar.maze_h
    rvar.hud_x = rvar.maze_w
    rvar.hud_y = 0
    xvar.win_w = rvar.maze_w + rvar.hud_w
    xvar.win_h = rvar.maze_h

    try:
        if xvar.win_w > xvar.screen_w:
            raise Exception(
                f"Generated {xvar.gen.output_file}, "
                "can't create window: window width > screen width "
                f"({xvar.win_w} > {xvar.screen_w})"
            )
        if xvar.win_h > xvar.screen_h - 50:
            raise Exception(
                f"Generated {xvar.gen.output_file},"
                "can't create window: window height > screen height"
                f"({xvar.win_h} > {xvar.screen_h})"
            )
        xvar.win = xvar.mlx.mlx_new_window(xvar.mlx_ptr,
                                           xvar.win_w,
                                           xvar.win_h,
                                           "MazeGenerator Visualizer"
                                           )
        if not xvar.win:
            raise Exception("Can't create window")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    xvar.main_img.img = xvar.mlx.mlx_new_image(
        xvar.mlx_ptr,
        xvar.win_w, xvar.win_h
    )
    xvar.main_img.width = xvar.win_w
    xvar.main_img.height = xvar.win_h
    (
        xvar.main_img.data,
        xvar.main_img.bpp,
        xvar.main_img.sl,
        xvar.main_img.iformat
    ) = xvar.mlx.mlx_get_data_addr(xvar.main_img.img)

    return (xvar, rvar)


def clear_img(img: ImgData, rvar: RenderingVar) -> None:
    """Clears the given image with current background color.

    Args:
        img (ImgData): Image to clear.
        rvar (RenderingVar): Rendering global variables.
    """
    for y in range(img.height):
        for x in range(img.width):
            put_pixel(img, x, y, rvar.color_palette.bg_color)


def put_pixel(img: ImgData, x: int, y: int, color: int) -> None:
    """Sets the pixel at x, y to the given color.

    Args:
        img (ImgData): Image to modify.
        x (int): X position.
        y (int): Y position.
        color (int): Color hex value.
    """
    if x < 0 or y < 0 or x >= img.width or y >= img.height:
        return
    bpp = img.bpp // 8
    pixel_index = x * bpp + y * img.sl
    img.data[pixel_index: pixel_index + bpp] = color.to_bytes(bpp, 'little')


def fill_cell(xvar: XVar,
              rvar: RenderingVar,
              cell_pos: Tuple[int, int],
              color: int
              ) -> None:
    """Fills the cell at cell_pos with the given color.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
        cell_pos (Tuple[int, int]): Tuple containing cell (col, row) position.
        color (int): Color hex value.
    """

    cell_col, cell_row = cell_pos
    for _ in range(rvar.cell_padding, rvar.cell_size - rvar.cell_padding + 1):
        for __ in range(
            rvar.cell_padding,
            rvar.cell_size - rvar.cell_padding + 1
        ):
            put_pixel(
                xvar.main_img,
                cell_col * rvar.cell_size + rvar.bd_thickness + _,
                cell_row * rvar.cell_size + rvar.bd_thickness + __,
                color
            )


def draw_full_grid(xvar: XVar, rvar: RenderingVar,) -> None:
    """Draws the full maze grid on the main image, with entry and exit cells,
    the 42 pattern and walls.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    fill_cell(xvar, rvar, xvar.gen.entry, 0xFF579812)
    fill_cell(xvar, rvar, xvar.gen.maze_exit, 0xFF728FF1)

    for x in range(rvar.maze_w):
        for t in range(rvar.bd_thickness):
            put_pixel(xvar.main_img, x, t, rvar.color_palette.wall_color)
            put_pixel(xvar.main_img,
                      x,
                      rvar.maze_h - rvar.bd_thickness + t,
                      rvar.color_palette.wall_color
                      )
    for y in range(rvar.maze_h + rvar.bd_thickness):
        for t in range(rvar.bd_thickness):
            put_pixel(xvar.main_img, t, y, rvar.color_palette.wall_color)
            put_pixel(xvar.main_img,
                      rvar.maze_w - rvar.bd_thickness + t,
                      y,
                      rvar.color_palette.wall_color
                      )

    for y, row in enumerate(xvar.gen.maze):
        for x, cell in enumerate(row):
            px = x * rvar.cell_size + rvar.bd_thickness
            py = y * rvar.cell_size + rvar.bd_thickness

            if cell.has_north_wall():
                for _ in range(rvar.cell_size):
                    put_pixel(xvar.main_img, px + _, py,
                              rvar.color_palette.wall_color)

            if cell.has_east_wall():
                for _ in range(rvar.cell_size):
                    put_pixel(xvar.main_img,
                              px + rvar.cell_size,
                              py + _,
                              rvar.color_palette.wall_color
                              )

            if cell.has_south_wall():
                for _ in range(rvar.cell_size):
                    put_pixel(xvar.main_img,
                              px + _,
                              py + rvar.cell_size,
                              rvar.color_palette.wall_color
                              )

            if cell.has_west_wall():
                for _ in range(rvar.cell_size):
                    put_pixel(xvar.main_img, px, py + _,
                              rvar.color_palette.wall_color)

    for pos in xvar.gen.pattern_42:
        fill_cell(xvar, rvar, pos, rvar.color_palette.pattern_color)

    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win, xvar.main_img.img, rvar.maze_x, rvar.maze_y
    )


def remove_wall(
        xvar: XVar,
        rvar: RenderingVar,
        cell_pos: Tuple[int, int],
        wall: int
        ) -> None:
    """Removes the wall of the given cell at cell_pos in the given direction.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
        cell_pos (Tuple[int, int]): Tuple containing cell (col, row) position.
        wall (int): Wall direction to remove.
    """
    col, row = cell_pos
    cell_x = col * rvar.cell_size + rvar.bd_thickness
    cell_y = row * rvar.cell_size + rvar.bd_thickness

    match wall:
        case Cell.NORTH:
            for _ in range(1, rvar.cell_size):
                put_pixel(
                    xvar.main_img,
                    cell_x + _, cell_y,
                    rvar.color_palette.bg_color
                    )
        case Cell.EAST:
            for _ in range(1, rvar.cell_size):
                put_pixel(xvar.main_img, cell_x + rvar.cell_size,
                          cell_y + _, rvar.color_palette.bg_color)
        case Cell.SOUTH:
            for _ in range(1, rvar.cell_size):
                put_pixel(xvar.main_img, cell_x + _,
                          cell_y + rvar.cell_size, rvar.color_palette.bg_color)
        case Cell.WEST:
            for _ in range(1, rvar.cell_size):
                put_pixel(
                    xvar.main_img,
                    cell_x, cell_y + _,
                    rvar.color_palette.bg_color
                    )
        case _:
            return


def draw_dfs_step(xvar: XVar,
                  rvar: RenderingVar,
                  step: Tuple[Tuple[int, int], int]
                  ) -> None:
    """Draws a step of the DFS maze generation algorithm.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
        step (Tuple[Tuple[int, int], int]): Current step containing
            cell position and wall direction.
    """
    current_cell, wall = step

    if (
        xvar.anim.prev_cell != xvar.gen.entry
        and xvar.anim.prev_cell != xvar.gen.maze_exit
    ):
        fill_cell(xvar, rvar, xvar.anim.prev_cell, rvar.color_palette.bg_color)
    if (
        current_cell != xvar.gen.entry
        and current_cell != xvar.gen.maze_exit
    ):
        fill_cell(xvar, rvar, current_cell, 0xFF4BBCE8)

    remove_wall(xvar, rvar, current_cell, wall)
    xvar.anim.prev_cell = current_cell


def draw_prim_step(xvar: XVar, rvar: RenderingVar, step: Any) -> None:
    """Draws a step of the Prim's maze generation algorithm.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
        step (Any): Current step containing cell position and wall direction.
    """
    current_cell, wall = step
    remove_wall(xvar, rvar, current_cell, wall)


def animate_dfs(param: Tuple[XVar, RenderingVar]) -> None:
    """Animates the DFS maze generation algorithm.

    Args:
        param (Tuple[XVar, RenderingVar]): Tuple containing XVar and
            RenderingVar instances.
    """
    xvar, rvar = param
    xvar.anim.tick += 1
    step = None

    try:
        if xvar.anim.tick % xvar.anim.speed == 0:
            step = next(xvar.anim.steps)
        else:
            return
    except StopIteration:
        xvar.anim.done = True
        clear_img(xvar.main_img, rvar)
        draw_full_grid(xvar, rvar)
        return

    draw_dfs_step(xvar, rvar, step)
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win, xvar.main_img.img, rvar.maze_x, rvar.maze_y
    )


def animate_prim(param: Tuple[XVar, RenderingVar]) -> None:
    """Animates the Prim's maze generation algorithm.

    Args:
        param (Tuple[XVar, RenderingVar]): Tuple containing XVar and
            RenderingVar instances.
    """
    xvar, rvar = param
    xvar.anim.tick += 1
    step = None

    try:
        if xvar.anim.tick % xvar.anim.speed == 0:
            step = next(xvar.anim.steps)
        else:
            return
    except StopIteration:
        xvar.anim.done = True
        clear_img(xvar.main_img, rvar)
        draw_full_grid(xvar, rvar)
        return

    draw_prim_step(xvar, rvar, step)
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win, xvar.main_img.img, rvar.maze_x, rvar.maze_y
    )


def draw_path_step(
        xvar: XVar, rvar: RenderingVar,
        current_path: List[Tuple[int, int]]
        ) -> None:
    """Draws the current step of the path finding algorithm.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
        current_path (List[Tuple[int, int]]): Current path cells.
    """
    COLOR_OLD = 0x33333333

    if hasattr(xvar.anim, 'old_path') and xvar.anim.old_path:
        for cell in xvar.anim.old_path:
            fill_cell(xvar, rvar, cell, COLOR_OLD)

    for _, cell in enumerate(current_path):
        fill_cell(xvar, rvar, cell, rvar.color_palette.path_color)

    xvar.anim.old_path = current_path


def animate_path_finding(param: Tuple[XVar, RenderingVar]) -> None:
    """Animates the path finding algorithm.

    Args:
        param (Tuple[XVar, RenderingVar]): Tuple containing XVar and
            RenderingVar instances.
    """
    xvar, rvar = param
    xvar.anim.tick += 1

    if hasattr(xvar.anim, 'steps') and not xvar.anim.path_done:
        if xvar.anim.tick % (xvar.anim.speed * 2) == 0:
            try:
                current_path = next(xvar.anim.steps)
                draw_path_step(xvar, rvar, current_path[1: -1])
            except StopIteration:
                xvar.anim.path_done = True
                clear_path_finding(xvar, rvar)
                draw_path_step(xvar, rvar, xvar.anim.old_path)
                return

    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win, xvar.main_img.img, rvar.maze_x, rvar.maze_y
    )


def clear_path_finding(xvar: XVar, rvar: RenderingVar) -> None:
    """Clears the path finding visualization from the maze.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    for y, row in enumerate(xvar.gen.maze):
        for x, _ in enumerate(row):
            if (x, y) != xvar.gen.entry and (x, y) != xvar.gen.maze_exit:
                if xvar.gen._is_not_42_pattern(x, y):
                    fill_cell(xvar, rvar, (x, y), rvar.color_palette.bg_color)


def generate_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the generate button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if xvar.anim and not xvar.anim.done:
        return

    clear_img(xvar.main_img, rvar)

    if xvar.gen.maze:
        xvar.gen.seed = randint(0, 100)

    if xvar.algo == "DFS":
        steps = xvar.gen.dfs_steps()
        first_step = next(steps)
        draw_full_grid(xvar, rvar)
        xvar.anim = Anim(steps)
        xvar.anim.prev_cell = first_step[0]
        xvar.mlx.mlx_loop_hook(xvar.mlx_ptr, animate_dfs, (xvar, rvar))
    elif xvar.algo == "PRIM":
        steps = xvar.gen.prim_steps()
        first_step = next(steps)
        draw_full_grid(xvar, rvar)
        xvar.anim = Anim(steps)
        xvar.mlx.mlx_loop_hook(xvar.mlx_ptr, animate_prim, (xvar, rvar))


def toggle_perfect_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the toggle perfect button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if xvar.anim and xvar.anim.done:
        xvar.gen.perfect = not xvar.gen.perfect
        btn = xvar.buttons[1]
        draw_button(xvar, btn)
        if xvar.gen.perfect:
            draw_text(
                xvar.hud_img,
                "IS PERFECT: YES",
                btn.x + 10, btn.y + btn.h // 2 - 10,
                0xFFFFFFFF
                )
        else:
            draw_text(
                xvar.hud_img,
                "IS PERFECT: NO",
                btn.x + 10, btn.y + btn.h // 2 - 10,
                0xFFFFFFFF
                )
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win, xvar.hud_img.img, rvar.hud_x, rvar.hud_y
        )


def change_algorithm_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the change algorithm button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    btn = xvar.buttons[2]
    draw_button(xvar, btn)
    if xvar.algo == "DFS":
        xvar.algo = "PRIM"
    else:
        xvar.algo = "DFS"
    draw_text(
        xvar.hud_img,
        xvar.algo,
        btn.x + 10, btn.y + btn.h // 2 - 10,
        0xFFFFFFFF
    )
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win, xvar.hud_img.img, rvar.hud_x, rvar.hud_y
    )


def find_path_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the find path button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if xvar.anim.done and not xvar.anim.path_done:
        xvar.anim.steps = xvar.gen.find_shortest_path_steps()
        xvar.mlx.mlx_loop_hook(
            xvar.mlx_ptr, animate_path_finding, (xvar, rvar)
        )


def toggle_path_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the toggle path button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    xvar.toggle_path_finding = not xvar.toggle_path_finding

    if xvar.toggle_path_finding and xvar.gen.path:
        draw_path_step(xvar, rvar, xvar.gen.path[1: -1])
    else:
        clear_path_finding(xvar, rvar)


def change_colors_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for change colors button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if xvar.gen.maze:
        rvar.palette_idx = (rvar.palette_idx + 1) % len(COLOR_PALETTES)
        rvar.color_palette = COLOR_PALETTES[rvar.palette_idx]
        clear_img(xvar.main_img, rvar)
        draw_full_grid(xvar, rvar)
    if xvar.gen.path and xvar.anim.path_done and xvar.toggle_path_finding:
        draw_path_step(xvar, rvar, xvar.gen.path[1: -1])


def inc_speed_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the increase speed button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if not xvar.anim:
        return

    if xvar.anim.speed > 1:
        xvar.anim.speed -= 1
    else:
        print("Animation speed min limit is reached: (speed >= 1)")


def dec_speed_oc(xvar: XVar, rvar: RenderingVar) -> None:
    """On click callback for the decrease speed button.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    if not xvar.anim:
        return

    if xvar.anim.speed <= 10:
        xvar.anim.speed += 1
    else:
        print("Animation speed max limit is reached: (speed <= 9)")


def init_buttons(xvar: XVar, rvar: RenderingVar) -> None:
    """Initializes the buttons and their on click callbacks.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    labels_and_ocs = [
        ("GENERATE", generate_oc),
        (
            "IS PERFECT: YES" if xvar.gen.perfect else "IS PERFECT: NO",
            toggle_perfect_oc
        ),
        ("DFS" if xvar.algo == "DFS" else "PRIM", change_algorithm_oc),
        ("FIND PATH", find_path_oc),
        ("TOGGLE PATH", toggle_path_oc),
        ("CHANGE COLORS", change_colors_oc),
        ("+ SPEED", inc_speed_oc),
        ("- SPEED", dec_speed_oc),
    ]

    btn_h = rvar.hud_h // len(labels_and_ocs)
    y = rvar.button_border
    for (label, on_click) in labels_and_ocs:
        xvar.buttons.append(
            Button(
                rvar.button_border,
                y,
                rvar.hud_w - rvar.button_border,
                btn_h - rvar.button_border,
                label,
                0xFF386FB0,
                on_click
            )
        )
        y += btn_h


def draw_text(
        img: ImgData,
        text: str, x: int, y: int,
        color: int, spacing: int = 1
        ) -> None:
    """Draws the given text on the image at position (x, y) with the
    given color. Uses the bitmapped font defined in FONT_LARGE.

    Args:
        img (ImgData): Image to draw the text on.
        text (str): Text to draw.
        x (int): X position.
        y (int): Y position.
        color (int): Color hex value.
        spacing (int, optional): Spacing between characters. Defaults to 1.
    """
    cx = x
    cy = y

    for c in text:
        glyph = FONT_LARGE.get(c)
        if glyph is None:
            cx += len(FONT_LARGE['A'][0])
            continue

        h = len(glyph)
        w = len(glyph[0])

        for j in range(h):
            for i in range(w):
                if glyph[j][i]:
                    put_pixel(
                        img,
                        cx + i,
                        cy + j,
                        color
                    )
        cx += w + spacing


def draw_button(xvar: XVar, btn: Button) -> None:
    """Draws the given button's rectangle on the HUD image.

    Args:
        xvar (XVar): XVar global variables.
        btn (Button): Button to draw.
    """
    for py in range(btn.y, btn.y + btn.h):
        for px in range(btn.x, btn.x + btn.w):
            put_pixel(xvar.hud_img, px, py, btn.color)


def draw_buttons(xvar: XVar, rvar: RenderingVar) -> None:
    """Draws all buttons on the HUD image.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    clear_img(xvar.hud_img, rvar)

    for btn in xvar.buttons:
        draw_button(xvar, btn)
        draw_text(
            xvar.hud_img,
            btn.label,
            btn.x + 10, btn.y + btn.h // 2 - 10,
            0xFFFFFFFF
            )

    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr,
        xvar.win,
        xvar.hud_img.img,
        rvar.hud_x,
        rvar.hud_y
    )


def text_width(text: str) -> int:
    """Calculates the width of the given text using the bitmapped font."""
    w = 0

    for c in text:
        w += len(FONT_LARGE[c][0]) + 1

    return w


def draw_intro_screen(xvar: XVar, rvar: RenderingVar) -> None:
    """Draws the intro screen with logo and contributors' names.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    try:
        result = xvar.mlx.mlx_png_file_to_image(
                    xvar.mlx_ptr,
                    "utils/images/logo-med.png"
                )
        if not result:
            raise Exception("Can't load PNG")
        xvar.logo_img.img, xvar.logo_img.width, xvar.logo_img.height = result
        if not xvar.logo_img.img:
            raise Exception("Can't create png")

        (
            xvar.logo_img.data,
            xvar.logo_img.bpp,
            xvar.logo_img.sl,
            xvar.logo_img.iformat,
        ) = xvar.mlx.mlx_get_data_addr(xvar.logo_img.img)
    except Exception as e:
        print(f"Error {e}")

    logo_x = (xvar.win_w - xvar.logo_img.width) // 2
    logo_y = (xvar.win_h - xvar.logo_img.height) // 5
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win,
        xvar.logo_img.img,
        logo_x,
        logo_y
    )

    lines = [
        "CONTRIBUTORS:",
        "BOUZKRAOUI ADNAN & SADOURI AYOUB",
        "PRESS ENTER TO START"
    ]

    y = logo_y + xvar.logo_img.height + 10
    for line in lines:
        x = (xvar.main_img.width - text_width(line)) // 2
        draw_text(xvar.main_img, line, x, y, rvar.color_palette.wall_color)
        y += 30
    xvar.mlx.mlx_put_image_to_window(
        xvar.mlx_ptr, xvar.win,
        xvar.main_img.img,
        0, 0
    )


def mouse_handler(
        mouse_button: int,
        x: int, y: int,
        param: Tuple[XVar, RenderingVar]
        ) -> None:
    """Mouse event handler.

    Args:
        mouse_button (int): Mouse button code.
        x (int): Mouse X position.
        y (int): Mouse Y position.
        param (Tuple[XVar, RenderingVar]): Tuple containing XVar and
            RenderingVar instances.
    """
    xvar, rvar = param

    hx = x - rvar.hud_x
    hy = y - rvar.hud_y

    if hx < 0 or hy < 0:
        return
    if mouse_button == 1:
        for btn in xvar.buttons:
            if btn.mouse_over(hx, hy):
                btn.on_click(xvar, rvar)


def key_handler(key: int, param: Tuple[XVar, RenderingVar]) -> None:
    """Keyboard key event handler.

    Args:
        key (int): Key code.
        param (Tuple[XVar, RenderingVar]): Tuple containing XVar and
            RenderingVar instances.
    """
    xvar, rvar = param
    if key == 65293 and xvar.status == Status.INTRO:
        xvar.status = Status.RUNNING
        visualizer(xvar, rvar)


def close_window(xvar: XVar) -> None:
    """Closes the window and exits the MLX loop.

    Args:
        xvar (XVar): XVar global variables.
    """
    xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)


def visualizer(xvar: XVar, rvar: RenderingVar) -> None:
    """Initializes the visualizer images, buttons and mouse event handler.

    Args:
        xvar (XVar): XVar global variables.
        rvar (RenderingVar): Rendering global variables.
    """
    xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win)
    xvar.main_img.img = xvar.mlx.mlx_new_image(
        xvar.mlx_ptr,
        rvar.maze_w, rvar.maze_h
    )
    xvar.main_img.width = rvar.maze_w
    xvar.main_img.height = rvar.maze_h
    (
        xvar.main_img.data,
        xvar.main_img.bpp,
        xvar.main_img.sl,
        xvar.main_img.iformat
    ) = xvar.mlx.mlx_get_data_addr(xvar.main_img.img)

    xvar.hud_img.img = xvar.mlx.mlx_new_image(
        xvar.mlx_ptr,
        rvar.hud_w, rvar.hud_h
    )
    xvar.hud_img.width = rvar.hud_w
    xvar.hud_img.height = rvar.hud_h
    (
        xvar.hud_img.data,
        xvar.hud_img.bpp,
        xvar.hud_img.sl,
        xvar.hud_img.iformat
    ) = xvar.mlx.mlx_get_data_addr(xvar.hud_img.img)

    init_buttons(xvar, rvar)
    draw_buttons(xvar, rvar)

    xvar.mlx.mlx_mouse_hook(xvar.win, mouse_handler, (xvar, rvar))


def launch_visualizer(config: Dict[str, Any]) -> None:
    """Launches the maze visualizer.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
    """
    xvar, rvar = init_params(config)

    draw_intro_screen(xvar, rvar)

    xvar.mlx.mlx_key_hook(xvar.win, key_handler, (xvar, rvar))
    xvar.mlx.mlx_hook(xvar.win, 33, 0, close_window, xvar)
    xvar.mlx.mlx_loop(xvar.mlx_ptr)

    if xvar.main_img.img:
        print("destroy main_img")
        xvar.mlx.mlx_destroy_image(xvar.mlx_ptr, xvar.main_img.img)
    if xvar.hud_img.img:
        print("destroy hud_img")
        xvar.mlx.mlx_destroy_image(xvar.mlx_ptr, xvar.hud_img.img)
    print("destroy win")
    xvar.mlx.mlx_destroy_window(xvar.mlx_ptr, xvar.win)
    print("destroy mlx")
    xvar.mlx.mlx_release(xvar.mlx_ptr)
