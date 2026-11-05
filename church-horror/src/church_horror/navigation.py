"""Camera motion and the classic wall-following tour."""

from dataclasses import dataclass
import math

from .config import Settings
from .maze import DELTAS, EAST, NORTH, SOUTH, WEST, Maze


def direction_yaw(direction: int) -> float:
    return (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)[direction]


@dataclass
class Camera:
    x: float = 0.5
    z: float = 0.5
    yaw: float = 0.0
    pitch: float = 0.0
    jump_height: float = 0.0


class Navigator:
    def __init__(self, maze: Maze, settings: Settings):
        self.maze = maze
        self.settings = settings
        self.camera = Camera()
        self.auto = True
        self.cell = (0, 0)
        self.facing = next(d for d in (EAST, SOUTH, NORTH, WEST) if not maze.has_wall(0, 0, d))
        self.camera.yaw = direction_yaw(self.facing)
        self._motion: tuple[str, float, float, float, float] | None = None
        self._step_after_turn = False

    def toggle_auto(self) -> None:
        self.auto = not self.auto
        self._motion = None
        self._step_after_turn = False
        if self.auto:
            self.cell = (int(self.camera.x), int(self.camera.z))
            self.facing = round(self.camera.yaw / (math.pi / 2)) % 4
            self.camera.x = self.cell[0] + 0.5
            self.camera.z = self.cell[1] + 0.5
            self.camera.yaw = direction_yaw(self.facing)

    def update_auto(self, dt: float) -> None:
        remaining = min(dt, 0.1)
        while remaining > 0:
            if self._motion is None:
                self._choose_motion()
            assert self._motion is not None
            kind, elapsed, duration, start, end = self._motion
            used = min(remaining, duration - elapsed)
            elapsed += used
            remaining -= used
            t = min(elapsed / duration, 1.0)
            smooth = t * t * (3 - 2 * t)
            if kind == "turn":
                self.camera.yaw = start + (end - start) * smooth
            else:
                dx, dz = DELTAS[self.facing]
                self.camera.x = self.cell[0] + 0.5 + dx * smooth
                self.camera.z = self.cell[1] + 0.5 + dz * smooth
            if elapsed >= duration - 1e-8:
                if kind == "turn":
                    self.camera.yaw = end % (2 * math.pi)
                    self.facing = round(end / (math.pi / 2)) % 4
                    self._step_after_turn = True
                else:
                    dx, dz = DELTAS[self.facing]
                    self.cell = (self.cell[0] + dx, self.cell[1] + dz)
                self._motion = None
            else:
                self._motion = (kind, elapsed, duration, start, end)

    def _choose_motion(self) -> None:
        x, z = self.cell
        if self._step_after_turn:
            self._step_after_turn = False
            self._motion = ("step", 0.0, self.settings.auto_step_seconds, 0.0, 1.0)
            return
        for offset in (1, 0, -1, 2):  # right, straight, left, back
            direction = (self.facing + offset) % 4
            if not self.maze.has_wall(x, z, direction):
                if offset:
                    # Keep turns short, including at dead ends.
                    angle = math.pi if offset == 2 else offset * math.pi / 2
                    self._motion = (
                        "turn", 0.0, self.settings.auto_turn_seconds,
                        self.camera.yaw, self.camera.yaw + angle,
                    )
                else:
                    self._motion = (
                        "step", 0.0, self.settings.auto_step_seconds, 0.0, 1.0,
                    )
                return
        raise RuntimeError("The current cell has no exit")

    def update_manual(self, dt: float, forward: float, strafe: float, turn: float) -> None:
        self.camera.yaw += turn * self.settings.turn_speed * dt
        length = math.hypot(forward, strafe)
        if length > 1:
            forward, strafe = forward / length, strafe / length
        yaw = self.camera.yaw
        dx = (math.sin(yaw) * forward + math.cos(yaw) * strafe) * self.settings.walk_speed * dt
        dz = (-math.cos(yaw) * forward + math.sin(yaw) * strafe) * self.settings.walk_speed * dt
        self._move_axis(dx, axis="x")
        self._move_axis(dz, axis="z")

    def _move_axis(self, amount: float, axis: str) -> None:
        if not amount:
            return
        radius = 0.16
        camera = self.camera
        x, z = int(camera.x), int(camera.z)
        if axis == "x":
            candidate = camera.x + amount
            if amount > 0 and candidate + radius >= x + 1 and self.maze.has_wall(x, z, EAST):
                candidate = x + 1 - radius
            elif amount < 0 and candidate - radius <= x and self.maze.has_wall(x, z, WEST):
                candidate = x + radius
            camera.x = max(radius, min(candidate, self.maze.width - radius))
        else:
            candidate = camera.z + amount
            if amount > 0 and candidate + radius >= z + 1 and self.maze.has_wall(x, z, SOUTH):
                candidate = z + 1 - radius
            elif amount < 0 and candidate - radius <= z and self.maze.has_wall(x, z, NORTH):
                candidate = z + radius
            camera.z = max(radius, min(candidate, self.maze.height - radius))
