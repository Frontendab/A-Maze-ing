*This project has been created as part of the 42 curriculum by asadouri and abouzkra*


# Description
### A-Maze-ing
A-Maze-ing is a lightweight Python project for generating, inspecting, and
exporting 2-D rectangular mazes. It provides a `MazeGenerator` class with two
randomized generation algorithms (depth-first backtracker and Prim), optional
dead-end braiding to introduce loops inside the maze, pathfinding utilities, and compact
exports suitable for simple visualizers.

**Key features**
- Generate perfect (no loops) or braided mazes.
- Deterministic generation via an optional `SEED`.
- Embedded "42" pattern for sufficiently large mazes (protected region).
- Step-wise generator APIs (`dfs_steps`, `prim_steps`) for animation.
- Shortest-path search and compact text/hex exports.

Requirements
- Python 3.10+ recommended (project uses `match` statements).
- Standard library only for core features. Optional visualization may require
	additional packages (see `utils/visualizer.py` and included MLX wheels).

# Instructions

### Installation
Create and activate a virtual environment and install dependencies:

```bash
make install
source .venv/bin/activate
```

### Quickstart (CLI)
1. Create a configuration file (example below).
2. Modify the name of the configuration file in `Makefile` if needed:
	```Makefile
	# Modify this line
	CONFIG_FILE = config.txt
	```
3. Run the CLI entry point:

	```bash
	make run
	```

	This will generate the maze, compute the shortest path, write outputs to the
configured file, and attempt to launch the visualizer if available.

### Cleaning up the project
Removes virtual environment `.venv` and temporary files or caches (e.g., __pycache__, .mypy__cache) to
keep the project environment clean.
```bash
make clean
```

### Check source file linting
Runs checks of source file static typing using mypy, and norm using flake8.
```bash
make lint
```

### Debugging the project
Run the main script in debug mode using pdb.
```bash
make debug
```

# Resources


# Additional Sections

## Configuration file format
The project parses a simple KEY=VALUE style configuration file (comments
starting with `#` are ignored). Required keys are `WIDTH`, `HEIGHT`, `ENTRY`,
`EXIT`, `OUTPUT_FILE`, and `PERFECT`. `SEED` is optional.

Example `config.txt`:

```text
WIDTH=21
HEIGHT=15
ENTRY=1,1
EXIT=19,13
OUTPUT_FILE=maze.txt
PERFECT=true
SEED=42
# Lines starting with # are ignored
```

- `ENTRY` and `EXIT` are comma-separated `x,y` integers (0-based coordinates).
- `PERFECT` accepts `true`/`1` or `false`/`0` (case-insensitive).

Notes about the embedded "42" pattern
- The fixed "42" pattern is only generated when both `WIDTH > 8` and
	`HEIGHT > 8`.
- The parser and generator will raise an error if `ENTRY` or `EXIT` falls
	inside the protected pattern.

## Maze generation algorithms
### Depth-First-Search algorithm
The depth-first search (recursive backtracker) algorithm carves passages by walking from a start cell, repeatedly choosing a random unvisited neighbor and backtracking when no neighbors remain. It produces perfect mazes with long, meandering corridors, runs in linear time relative to the number of cells, and maps naturally to the provided step-wise API for smooth generation animation.
The exact steps are explained bellow:

1. Initialize grid: create Cell objects for each coordinate; set all walls present and visited=False.
2. Set the seed RNG.
3. Choose the start cell (entry or a default); mark it visited and push it on a stack.
4. While stack is not empty:
	- Let current = stack[-1].
	- Collect current’s unvisited neighbors (N/E/S/W within bounds, not visited, not inside protected pattern).
	- If there are unvisited neighbors:
		- Choose one neighbor at random.
		- Remove the walls between current and chosen neighbor (update both cells’ wall bitflags).
		- Mark the neighbor visited.
		- Push the neighbor onto the stack.
		- Yield a generation step (wall removals and the new current).
	- Else:
    	- Pop the stack (backtrack).
    	- Yield a backtrack step if the step generator reports it.
    	- When the stack is empty the maze is complete (perfect — no cycles).
    	- Optionally (if braiding is enabled and perfect=False) post-process to braid selected dead-ends (not part of a perfect maze).
5. When the stack is empty the maze is complete (perfect — no cycles).
6. Optionally (if braiding is enabled and perfect=False) post-process to braid selected dead-ends (not part of a perfect maze).

### Prim's algorithm
Prim’s algorithm builds the maze by maintaining a frontier of candidate walls and repeatedly connecting a random frontier cell to the existing maze, producing more evenly distributed, “bushier” mazes with shorter average path lengths than DFS. Like DFS, the implementation yields perfect mazes without braiding, supports deterministic seeding.
The exact steps are explained bellow:

1. Initialize grid: create Cell objects for each coordinate; set all walls present and visited=False.
2. Set the seed RNG.
3. Choose an initial cell; mark it visited.
4. Add that cell’s unvisited neighbors to a frontier set/list.
5. While frontier is not empty:
	- Choose a frontier cell at random from the frontier.
	- From that frontier cell, collect its neighboring cells that are already visited (one or more).
	- Choose one visited neighbor at random.
	- Remove the wall between the frontier cell and the chosen visited neighbor (update both cells’ wall bitflags).
	- Mark the frontier cell visited.
	- Add the frontier cell’s unvisited neighbors (not already in frontier) to the frontier.
	- Remove the processed cell from frontier.
	- Yield a generation step (frontier selection and wall removal).
6. When frontier is empty the maze is complete (perfect — no cycles).
7. Optionally (if braiding is enabled and perfect=False) post-process to braid dead-ends (not part of a perfect maze).

### DFS algorithm choice explanation
DFS (recursive backtracker) was chosen for its simplicity, efficiency, and the classic maze aesthetic it produces: long winding corridors and pronounced dead-ends. It runs in linear time, maps directly to a step-wise/stack-based implementation that is easy to animate and reason about, and yields deterministic results when seeded—making it ideal for teaching, visualization, and use cases where that distinctive maze character is desired.

### Prim's algorithm choice explanation
Prim’s algorithm was included to offer a contrasting maze topology: more evenly distributed passages and shorter average path lengths, producing “bushier” layouts than DFS. Its frontier-based approach also animates naturally and deterministically with a seed, giving users an alternative generation style and complementary visual/solving behaviors to suit different preferences or testing scenarios.

## Reusable Code
You can use the library directly from Python:

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
		width=21,
		height=15,
		entry=(1, 1),
		maze_exit=(19, 13),
		seed=42,	# optional
		output_file="maze.txt",
		perfect=True,
)

# Synchronous generation (saves into gen.maze)
gen.dfs()              # or gen.prim()

# To access the generated maze
gen.maze

# Compute shortest path (saves into gen.path)
gen.find_shortest_path()

# To access the generated path
gen.path

# Stringifying the generation results
print(gen.maze_to_str())  # maze as hexadecimal wall representation
print(gen.path_to_str())  # compass directions string (N/S/E/W)
```

API notes
- `dfs_steps()` and `prim_steps()` return generators that yield step events
	suitable for animating a visualizer.
- `maze_to_str()` returns a multi-line string where each cell is represented
	by a compact hexadecimal value (bitflags of walls). `path_to_str()` returns
	a sequence of `N`, `S`, `E`, `W` moves between consecutive cells.

## Project management

### Roles of each member
- `asadouri` — Config file parsing, Prim's algorithm and animation, shortest-path logic and animation, modularization, Makefile and overall project structure.
- `abouzkra` — Cell model, MazeGenerator core structure, DFS algorithm and animation, visualizer design and UI (buttons).

### Project planning
Work was organized around small, focused milestones: core maze model, generation algorithms (DFS / Prim), step-wise APIs for animation, pathfinding, visualizer integration, and CLI/export utilities. Tasks were implemented iteratively with frequent local testing and incremental integration via the Makefile. Priorities were correctness, reproducibility (seeded RNG), and a compact export format for easy visualization.

### What worked well and what could be improved
- What worked well:
  - Clear division of responsibilities enabled parallel development.
  - Step-wise generator APIs made animation and testing straightforward.
  - Deterministic seeding and compact exports simplified debugging and reproducibility.
  - Lightweight, standard-library-first implementation keeps dependencies minimal.
- Improvements:
  - Add more unit tests and continuous integration to catch regressions early.
  - Expand documentation with more usage examples and visualizer screenshots.
  - Add automated packaging / release workflow (Poetry/pyproject or CI pipeline).
  - Improve performance for very large mazes and harden edge-case validation.

### Specific tool usage
- virtualenv / .venv — Isolate the development environment.
- Makefile — Common tasks (install, run, lint, clean) are exposed via make targets.
- Poetry (optional) — Recommended for packaging and dependency management if the project is expanded.
- MLX / visualizer assets — Optional runtime for the visualizer; included wheels are used when available.
- flake8 / mypy — Static checks for code style and typing.

## Advanced Features
### Visualizer Buttons
The visualizer exposes simple controls to inspect and interact with generation and solving in real time:

- Generate: run the step-wise generator to generate the next maze.
- Algorithm Selector: switch between DFS and Prim animation modes.
- Braiding Toggle: enable/disable post-processing that braids dead-ends (show effect immediately).
- Path finding: run the step-wise generator to animate path finding in the current maze.
- Path toggle: Show/Hide the path.
- Speed Control: adjust animation speed (step delay) to slow down or speed up playback.

Note: the visualizer is optional and requires the MLX/visualizer runtime; when unavailable the CLI still produces export files.

### Visualizer Animation overview
Animations are driven by the library’s step-wise generators (dfs_steps and prim_steps). Each step event updates a small, focused set of changes (current cell, newly visited cell, removed wall, frontier updates), which the UI renders incrementally for smooth, memory-efficient playback. Visual cues include:

- Current cell highlight and visited-cell shading.
- Wall removals animated as they happen.
- For DFS: stack/backtrack transitions are visible so backtracking becomes obvious.
- For Prim: frontier cells are highlighted and connections to the existing maze are animated.
- Final shortest-path overlay shows the computed solution after generation completes.

This design makes it easy to compare algorithm behavior, debug generation logic, and create instructional animations. For very large mazes, reduce animation speed or skip frame rendering to keep the UI responsive.