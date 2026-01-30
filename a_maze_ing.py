"""A-Maze-ing: CLI entry point for 2-D maze generation and visualization.

This module provides the main command-line interface for the A-Maze-ing
project. It reads configuration from a file, instantiates a MazeGenerator,
runs maze generation and pathfinding, exports results to disk, and optionally
launches a visualizer.

Usage:
    python3 a_maze_ing.py <config_file>

The config file should specify WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, and
OUTPUT_FILE settings. SEED is optional for deterministic generation.
"""

from typing import Dict
from mazegen import MazeGenerator
from utils import return_config, launch_visualizer
import sys

from utils import write_output


def main() -> None:
    """Parse config, generate maze, find shortest path, and export results.

    Reads configuration from a command-line specified file, creates a
    MazeGenerator, runs DFS-based maze generation, computes the shortest
    path, writes output, and launches the visualizer if configured.

    Exits with error code 1 if MazeGenerator construction or any operation
    fails.
    """
    print("=== A-Maze-ing ===")

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        return

    config_file = sys.argv[1]
    config: Dict = {}
    try:
        config = return_config(config_file)
    except ValueError as e:
        print(f"Error: {e}")
        return

    gen = None
    try:
        if 'SEED' in config.keys():
            gen = MazeGenerator(
                config['WIDTH'], config['HEIGHT'],
                config['ENTRY'], config['EXIT'],
                config['SEED'], config['OUTPUT_FILE'],
                config['PERFECT']
                )
        else:
            gen = MazeGenerator(
                config['WIDTH'], config['HEIGHT'],
                config['ENTRY'], config['EXIT'],
                None, config['OUTPUT_FILE'],
                config['PERFECT']
                )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    gen.dfs()
    gen.find_shortest_path()
    write_output(gen)

    launch_visualizer(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
