"""Maze generation utilities and the MazeGenerator implementation.

This module provides the MazeGenerator class, which encapsulates all
responsibilities needed to construct 2-D rectangular mazes. It implements
multiple generation algorithms (depth-first backtracker and Prim's algorithm),
manages low-level cell and wall state, validates inputs (dimensions, entry/exit
points, seed, output path, and flags), enforces an optional fixed "42" pattern
region, and offers pathfinding and export/visualization helpers. The generator
supports deterministic output through a seed and an option to introduce loops
by braiding dead-ends when a perfect maze is not required.

Classes:
    MazeGenerator: Create, configure, and generate mazes; provides step-wise
    generators for visualizers and synchronous generation methods.

Usage:
    Instantiate MazeGenerator with width, height, entry, exit, seed,
    output_file, and perfect flag. Call dfs() or prim() to build the
    maze, or iterate dfs_steps() / prim_steps() to animate generation.
"""

from random import seed, randint
from typing import Any, List, Optional, Tuple, Generator
from .models import Cell
import heapq


class MazeGenerator:

    """Create and manage 2-D rectangular mazes.

    The MazeGenerator class encapsulates maze construction, validation,
    pattern enforcement, generation algorithms (DFS and Prim), optional
    dead-end braiding, pathfinding, and simple export helpers.

    Attributes:
        width (int): Maze width in cells.
        height (int): Maze height in cells.
        entry (Tuple[int, int]): Entrance cell coordinates (x, y).
        maze_exit (Tuple[int, int]): Exit cell coordinates (x, y).
        seed (int): Random seed used for deterministic generation.
        output_file (str): Suggested output filename for exports.
        perfect (bool): If True, generate a perfect maze (no loops).
        pattern_42 (List[Tuple[int, int]]): Protected coordinates for the
            fixed "42" pattern embedded in sufficiently large mazes.
        maze (List[List[Cell]]): Internal grid of Cell objects.
        path (List[Tuple[int, int]]): Last-computed shortest path (excluding
            entry/exit) as a list of coordinates.
    """

    DIRECTIONS = [
        (0, -1, Cell.NORTH, Cell.SOUTH),
        (1, 0, Cell.EAST, Cell.WEST),
        (0, 1, Cell.SOUTH, Cell.NORTH),
        (-1, 0, Cell.WEST, Cell.EAST)
    ]

    def __init__(
            self,
            width: int, height: int,
            entry: Tuple[int, int],
            maze_exit: Tuple[int, int],
            output_file: str,
            perfect: bool,
            seed: Optional[int] = randint(0, 100)
            ) -> None:
        """Initialize a new MazeGenerator instance.

        Args:
            width: Number of columns in the maze (must be >= 3).
            height: Number of rows in the maze (must be >= 3).
            entry: (x, y) coordinates for the maze entrance.
            maze_exit: (x, y) coordinates for the maze exit.
            seed: Optional integer seed for deterministic RNG. If None, a
                random seed is chosen.
            output_file: Suggested filename for writing exported output.
            perfect: If True, produce a perfect maze (no additional loops).

        Raises:
            TypeError, ValueError: On invalid inputs (delegates to
                _validate_inputs).
        """
        MazeGenerator._validate_inputs(
            width, height,
            entry, maze_exit, seed,
            output_file, perfect
        )
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.maze_exit: Tuple[int, int] = maze_exit
        self.seed: int = seed if seed else self.seed
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.pattern_42: List[Tuple[int, int]] = self._generate_pattern_42()
        self.maze: List[List[Cell]] = []
        self.path: List[Tuple[int, int]] = []

    @staticmethod
    def _validate_inputs(
            width: int, height: int,
            entry: Tuple[int, int],
            maze_exit: Tuple[int, int],
            seed: Optional[int],
            output_file: str,
            perfect: bool
                        ) -> None:
        """Validate constructor arguments for type and value constraints.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: Entrance coordinate tuple.
            maze_exit: Exit coordinate tuple.
            seed: Optional RNG seed.
            output_file: Output filename.
            perfect: Perfect-flag boolean.

        Raises:
            TypeError: If argument types are incorrect.
            ValueError: If numeric values are out of allowed ranges or
                coordinates fall outside the maze bounds.
        """
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and hight must be integers!")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be greater than 0!")
        if width < 3 or height < 3:
            raise ValueError(
                f"Cannot generate a valid maze with {width, height}\n" +
                "A valid maze must be at least 3x3!"
            )

        # entry and exit coordinates validation
        for name, point in {'entry': entry, 'maze_exit': maze_exit}.items():
            if (
                not isinstance(point, tuple)
                or len(point) != 2
                or not all(isinstance(coord, int) for coord in point)
            ):
                raise TypeError(f"{name} must be a tuple of two integers!")

            x, y = point
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"{name} {point} is out of maze dimentions!")

        if entry == maze_exit:
            raise ValueError("Entry and exit should be different cells")

        # seed value validation
        if seed:
            if not isinstance(seed, int):
                raise TypeError("Seed value must be an integer!")
            if seed < 0:
                raise ValueError("Seed value must be greater than 0!")

        # output file name validation
        if not isinstance(output_file, str):
            raise TypeError("Output file name must be a string!")

        # perfect flag validation
        if not isinstance(perfect, bool):
            raise TypeError("Perfect flag must be a boolean (True/False)!")

    def _generate_grid(self) -> List[List[Cell]]:
        """Create a fresh grid of unvisited Cell objects.

        Returns:
            A 2-D list (height x width) of newly constructed Cell
            instances.
        """
        return [[Cell() for _ in range(self.width)]
                for _ in range(self.height)]

    def _generate_pattern_42(self) -> List[Tuple[int, int]]:
        """Generate coordinates for the fixed '42' pattern region.

        The pattern is only created for sufficiently large mazes. The method
        validates that the configured entry and maze_exit are not
        placed inside the pattern.

        Returns:
            A list of (x, y) coordinates belonging to the pattern.

        Raises:
            ValueError: If the maze is too small to contain the pattern or if
                the entry/exit fall inside the pattern.
        """
        if self.width > 8 and self.height > 8:
            pattern_x = int((self.width - 7) / 2)
            pattern_y = int((self.height - 5) / 2)

            pattern = [
                (pattern_x, pattern_y),
                (pattern_x, pattern_y + 1),
                (pattern_x, pattern_y + 2),
                (pattern_x + 1, pattern_y + 2),
                (pattern_x + 2, pattern_y + 2),
                (pattern_x + 2, pattern_y + 3),
                (pattern_x + 2, pattern_y + 4),
                (pattern_x + 4, pattern_y),
                (pattern_x + 4, pattern_y + 2),
                (pattern_x + 4, pattern_y + 3),
                (pattern_x + 4, pattern_y + 4),
                (pattern_x + 5, pattern_y),
                (pattern_x + 5, pattern_y + 2),
                (pattern_x + 5, pattern_y + 4),
                (pattern_x + 6, pattern_y),
                (pattern_x + 6, pattern_y + 1),
                (pattern_x + 6, pattern_y + 2),
                (pattern_x + 6, pattern_y + 4)
            ]
            if self.entry in pattern:
                raise ValueError("Entry point is inside 42 pattern!")
            if self.maze_exit in pattern:
                raise ValueError("Exit point is inside 42 pattern!")
            return pattern
        else:
            raise ValueError("Cannot generate 42 pattern, maze too small!")

    def _is_not_42_pattern(self, x: int, y: int) -> bool:
        """Return True if the given coordinate is not part of the 42 pattern.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True when (x, y) is not in self.pattern_42.
        """
        return (
            all((x, y) != p for p in self.pattern_42)
        )

    def _in_maze_bounds(self, x: int, y: int) -> bool:
        """Check whether a coordinate is inside the maze and not in pattern.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if the coordinate is within (0..width-1, 0..height-1)
            and is not part of the protected 42 pattern.
        """
        return (
            0 <= x < self.width and 0 <= y < self.height
            and self._is_not_42_pattern(x, y)
        )

    def _remove_wall(self, cell: Cell, wall: int) -> None:
        """Remove the specified wall from a Cell instance.

        Args:
            cell: Target Cell whose wall will be removed.
            wall: Wall constant from Cell (e.g. Cell.NORTH).
        """
        if wall == Cell.NORTH:
            cell.remove_north_wall()
        elif wall == Cell.EAST:
            cell.remove_east_wall()
        elif wall == Cell.SOUTH:
            cell.remove_south_wall()
        elif wall == Cell.WEST:
            cell.remove_west_wall()

    def _wall_count(self, cell: Cell) -> int:
        """Return the number of intact walls for a given Cell.

        Args:
            cell: The Cell to inspect.

        Returns:
            Integer count of walls currently present on the cell (0-4).
        """
        return sum([
            cell.has_east_wall(),
            cell.has_north_wall(),
            cell.has_south_wall(),
            cell.has_west_wall()
        ])

    def braid_dead_ends(self) -> None:
        """Introduce loops by braiding (connecting) some dead-end cells.

        This method randomly selects neighboring cells for dead-ends and
        removes a wall to reduce the number of pure dead-ends, which creates
        mazes that are not strictly perfect.
        """
        seed(self.seed)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self._is_not_42_pattern(x, y):
                    continue

                cell = self.maze[y][x]
                if self._wall_count(cell) == 3:
                    neighbors = []

                    for dx, dy, wall, op_wall in MazeGenerator.DIRECTIONS:
                        nx, ny = x + dx, y + dy
                        if self._in_maze_bounds(nx, ny):
                            neighbors.append((nx, ny, wall, op_wall))

                    if neighbors:
                        (
                            nx, ny,
                            wall, op_wall
                        ) = neighbors[randint(0, len(neighbors) - 1)]
                        self._remove_wall(cell, wall)
                        self._remove_wall(self.maze[ny][nx], op_wall)

    def dfs_steps(self) -> Generator[Any, None, None]:
        """Generate the maze using Depth-First-Search algorithm as a
        generator.

        Yields:
            Tuples describing wall removals for visualization or stepwise
            consumers.
        """
        seed(self.seed)
        self.maze = self._generate_grid()
        yield (self.entry, -1)

        start_x, start_y = self.entry
        stack = [self.entry]
        self.maze[start_y][start_x].set_visited(True)

        while stack:
            x, y = stack[-1]
            current = self.maze[y][x]

            neighbors = []
            for dir_x, dir_y, wall, op_wall in MazeGenerator.DIRECTIONS:
                next_x, next_y = x + dir_x, y + dir_y
                if (
                    self._in_maze_bounds(next_x, next_y)
                    and not self.maze[next_y][next_x].visited()
                ):
                    neighbors.append((next_x, next_y, wall, op_wall))

            if not neighbors:
                stack.pop()
                continue

            idx = randint(0, len(neighbors) - 1)
            next_x, next_y, wall, op_wall = neighbors[idx]

            neighbor = self.maze[next_y][next_x]
            self._remove_wall(current, wall)
            self._remove_wall(neighbor, op_wall)

            yield ((x, y), wall)
            neighbor.set_visited(True)
            stack.append((next_x, next_y))

        if not self.perfect:
            self.braid_dead_ends()

    def dfs(self) -> None:
        """Synchronous wrapper that runs the full DFS maze generation.

        This consumes the generator returned by dfs_steps until
        completion.
        """
        steps = self.dfs_steps()

        try:
            while True:
                _ = next(steps)
        except StopIteration:
            return

    def prim_steps(self) -> Generator[Any, None, None]:
        """Generate the maze using Prim's randomized algorithm as a
        generator.

        Yields:
            Tuples describing wall removals for visualization or stepwise
            consumers.
        """
        self.maze = self._generate_grid()
        start_x, start_y = self.entry
        seed(self.seed)

        yield (self.entry, -1)

        frontier = []

        def add_to_frontier(x: int, y: int) -> None:
            for dx, dy, wall, op_wall in MazeGenerator.DIRECTIONS:
                next_x, next_y = x + dx, y + dy
                if (
                    self._in_maze_bounds(next_x, next_y)
                    and not self.maze[next_y][next_x].visited()
                ):
                    frontier.append((x, y, next_x, next_y, wall, op_wall))

        self.maze[start_y][start_x].set_visited(True)
        add_to_frontier(start_x, start_y)

        while frontier:
            idx = randint(0, len(frontier) - 1)
            curr_x, curr_y, next_x, next_y, wall, op_wall = frontier.pop(idx)

            if not self.maze[next_y][next_x].visited():
                self._remove_wall(self.maze[curr_y][curr_x], wall)
                self._remove_wall(self.maze[next_y][next_x], op_wall)

                self.maze[next_y][next_x].set_visited(True)
                add_to_frontier(next_x, next_y)

                yield ((curr_x, curr_y), wall)

        if not self.perfect:
            self.braid_dead_ends()

    def prim(self) -> None:
        """Synchronous wrapper that runs Prim's generation until completion."""
        steps = self.prim_steps()

        try:
            while True:
                next(steps)
        except StopIteration:
            return

    def find_shortest_path_steps(
            self
            ) -> Generator[List[Tuple[int, int]], None, None]:
        """Find the shortest path between entry and exit using Dijkstra.

        Yields:
            Intermediate path lists (excluding entry/exit) as the search
            progresses; final assignment is saved to self.path.
        """
        if not self.maze:
            print("No path can be provided, generate maze first!")
            return
        start = self.entry
        end = self.maze_exit

        pq = [(0, start, [start])]

        distance = {start: 0}
        while pq:
            current_cost, (curr_x, curr_y), path = heapq.heappop(pq)

            yield path

            if (curr_x, curr_y) == end:
                self.path = path
                return

            if current_cost > distance.get((curr_x, curr_y), float('inf')):
                continue

            current_cell = self.maze[curr_y][curr_x]

            directions = [
                (0, -1, current_cell.has_north_wall()),
                (1, 0, current_cell.has_east_wall()),
                (0, 1, current_cell.has_south_wall()),
                (-1, 0, current_cell.has_west_wall())
            ]

            for dx, dy, has_wall in directions:
                nx, ny = curr_x + dx, curr_y + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height and not has_wall
                ):
                    new_cost = current_cost + 1
                    if new_cost < distance.get((nx, ny), float('inf')):
                        distance[(nx, ny)] = new_cost
                        heapq.heappush(
                            pq,
                            (new_cost, (nx, ny), path + [(nx, ny)])
                        )

    def find_shortest_path(self) -> None:
        """Synchronous wrapper that runs the shortest-path search to
        completion and stores the resulting path in self.path."""
        steps = self.find_shortest_path_steps()

        try:
            while True:
                next(steps)
        except StopIteration:
            return

    def maze_to_str(self) -> str:
        """Return a compact string representation of the maze grid.

        Each cell is represented by its hexadecimal string as produced by
        Cell.to_hex() and rows are joined with newlines.

        Returns:
            A multi-line string representing the maze grid.
        """
        return "\n".join(
            "".join(cell.to_hex() for cell in row)
            for row in self.maze
        )

    def path_to_str(self) -> str:
        """Return the last-computed path as a compass-direction string.

        The path is converted to a sequence of characters where "N", "S",
        "E", and "W" denote moves between consecutive cells. If no path is
        available an empty string is returned and a message is printed.

        Returns:
            Direction string (e.g. "NNEESW") or an empty string when no path
            is present.
        """
        if not self.path:
            return ""

        path_as_str = ""

        prev = self.path[0]
        for x, y in self.path[1:]:
            direction = (x - prev[0], y - prev[1])
            match direction:
                case (0, -1):
                    path_as_str += "N"
                case (0, 1):
                    path_as_str += "S"
                case (1, 0):
                    path_as_str += "E"
                case (-1, 0):
                    path_as_str += "W"
            prev = (x, y)
        return path_as_str
