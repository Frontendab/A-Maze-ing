
"""mazegen package — simple 2-D maze generation utilities.

This package exposes the Cell model and the MazeGenerator class for
creating, inspecting, and exporting rectangular mazes. It provides both
synchronous and step-wise generation APIs, deterministic seeding, and
helpers for pathfinding and visualization.

Public exports:
    - Cell: Lightweight cell model with wall bitflags and helpers.
    - MazeGenerator: High-level generator implementing DFS and Prim,
    optional braiding, pathfinding, and compact export helpers.

Example:
    from mazegen import MazeGenerator, Cell
"""

from .models import Cell
from .generator import MazeGenerator

__all__ = ["Cell", "MazeGenerator"]
