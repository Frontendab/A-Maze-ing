"""Export maze data to an output file.

This module provides utilities for writing a MazeGenerator instance's
results (maze grid, entry/exit points, and computed path) to a file in a
compact text format.

Functions:
    write_output: Write maze and path data from a generator to disk.
"""

from mazegen import MazeGenerator


def write_output(gen: MazeGenerator) -> None:
    """Writes the maze, entry and exit points and path to the output file.

    Args:
        gen (MazeGenerator): Instance of Mazegenerator containing maze data.
    """
    with open(gen.output_file, 'w') as f:
        f.write(gen.maze_to_str())
        f.write("\n\n")
        f.write(f"{gen.entry[0]}, {gen.entry[1]}\n")
        f.write(f"{gen.maze_exit[0]}, {gen.maze_exit[1]}\n")
        f.write(gen.path_to_str() + "\n")

    gen.maze = []
