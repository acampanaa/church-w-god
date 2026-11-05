"""Pure maze model; no rendering or input dependencies."""

from collections import deque
from dataclasses import dataclass
import random


# Direction order is north, east, south, west.
NORTH, EAST, SOUTH, WEST = range(4)
DELTAS = ((0, -1), (1, 0), (0, 1), (-1, 0))


@dataclass
class Maze:
    width: int
    height: int
    walls: list[list[int]]

    @classmethod
    def generate(cls, width: int, height: int, seed: int | None = None) -> "Maze":
        if width < 2 or height < 2:
            raise ValueError("Maze dimensions must be at least 2 by 2")
        rng = random.Random(seed)
        maze = cls(width, height, [[0b1111 for _ in range(width)] for _ in range(height)])
        visited = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            x, z = stack[-1]
            choices = []
            for direction, (dx, dz) in enumerate(DELTAS):
                neighbor = (x + dx, z + dz)
                if maze.contains(*neighbor) and neighbor not in visited:
                    choices.append((direction, neighbor))
            if not choices:
                stack.pop()
                continue
            direction, (nx, nz) = rng.choice(choices)
            maze.walls[z][x] &= ~(1 << direction)
            maze.walls[nz][nx] &= ~(1 << ((direction + 2) % 4))
            visited.add((nx, nz))
            stack.append((nx, nz))
        return maze

    def contains(self, x: int, z: int) -> bool:
        return 0 <= x < self.width and 0 <= z < self.height

    def has_wall(self, x: int, z: int, direction: int) -> bool:
        if not self.contains(x, z):
            return True
        return bool(self.walls[z][x] & (1 << direction))

    def reachable_count(self, start: tuple[int, int] = (0, 0)) -> int:
        seen = {start}
        queue = deque([start])
        while queue:
            x, z = queue.popleft()
            for direction, (dx, dz) in enumerate(DELTAS):
                next_cell = (x + dx, z + dz)
                if not self.has_wall(x, z, direction) and next_cell not in seen:
                    seen.add(next_cell)
                    queue.append(next_cell)
        return len(seen)
