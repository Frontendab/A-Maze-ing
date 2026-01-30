class Cell:
    """Representation of a single maze cell and its four walls.

    Walls are stored as bitflags on self._walls using the constants
    NORTH, EAST, SOUTH, and WEST. The cell also tracks a
    visited flag used by generation algorithms.

    Attributes:
        _walls (int): Bitfield representing present walls (1 == present).
        _is_visited (bool): Whether the cell has been visited during carving.
    """

    NORTH: int = 0b0001
    EAST: int = 0b0010
    SOUTH: int = 0b0100
    WEST: int = 0b1000

    def __init__(self) -> None:
        """Create a cell with all four walls present and unvisited state.

        The default wall bitfield is set so that every side is initially
        closed; generation algorithms remove walls to carve passages.
        """
        self._walls: int = 0b1111
        self._is_visited: bool = False

    def add_north_wall(self) -> None:
        """Adds the north wall to this cell."""
        self._walls |= Cell.NORTH

    def add_east_wall(self) -> None:
        """Adds the east wall to this cell."""
        self._walls |= Cell.EAST

    def add_south_wall(self) -> None:
        """Adds the south wall to this cell."""
        self._walls |= Cell.SOUTH

    def add_west_wall(self) -> None:
        """Adds the west wall to this cell."""
        self._walls |= Cell.WEST

    def remove_north_wall(self) -> None:
        """Remove the north wall (open passage to the north)."""
        self._walls &= ~Cell.NORTH

    def remove_east_wall(self) -> None:
        """Remove the east wall (open passage to the east)."""
        self._walls &= ~Cell.EAST

    def remove_south_wall(self) -> None:
        """Remove the south wall (open passage to the south)."""
        self._walls &= ~Cell.SOUTH

    def remove_west_wall(self) -> None:
        """Remove the west wall (open passage to the west)."""
        self._walls &= ~Cell.WEST

    def has_north_wall(self) -> bool:
        """Return True when the north wall is present."""
        return bool(self._walls & Cell.NORTH)

    def has_east_wall(self) -> bool:
        """Return True when the east wall is present."""
        return bool(self._walls & Cell.EAST)

    def has_south_wall(self) -> bool:
        """Return True when the south wall is present."""
        return bool(self._walls & Cell.SOUTH)

    def has_west_wall(self) -> bool:
        """Return True when the west wall is present."""
        return bool(self._walls & Cell.WEST)

    def visited(self) -> bool:
        """Return whether this cell has been visited by a generator."""
        return self._is_visited

    def set_visited(self, value: bool) -> None:
        """Set the visited flag for this cell.

        Args:
            value: Boolean visited state to assign.
        """
        self._is_visited = value

    def to_hex(self) -> str:
        """Return a compact hexadecimal representation of the wall bitfield.

        Returns:
            Uppercase hex string representing the current wall bits.
        """
        return hex(self._walls)[2:].upper()

    def draw(self) -> None:
        """Placeholder for rendering logic used by visualizers.

        Implementations may draw the cell to a canvas or terminal. The
        default implementation is a no-op.
        """
        pass
