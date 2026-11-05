"""Walkable church floor plan and first-person movement, without graphics code."""

from dataclasses import dataclass
import math

from .navigation import Camera


@dataclass(frozen=True)
class Rectangle:
    left: float
    front: float
    right: float
    back: float

    def touches_circle(self, x: float, z: float, radius: float) -> bool:
        nearest_x = max(self.left, min(x, self.right))
        nearest_z = max(self.front, min(z, self.back))
        return (x - nearest_x) ** 2 + (z - nearest_z) ** 2 < radius ** 2


class ChurchWorld:
    half_width = 7.0
    length = 26.0
    player_radius = 0.25

    def __init__(self) -> None:
        self.columns = tuple(
            Rectangle(x - 0.38, z - 0.38, x + 0.38, z + 0.38)
            for x in (-4.6, 4.6)
            for z in (7.0, 12.0, 17.0, 22.0)
        )
        self.iconostasis = (
            Rectangle(-6.85, 3.65, -1.25, 3.95),
            Rectangle(1.25, 3.65, 6.85, 3.95),
        )
        self.furniture = (
            Rectangle(-1.2, 0.9, 1.2, 2.2),  # altar table
            Rectangle(-2.8, 5.0, -2.1, 5.7),
            Rectangle(2.1, 5.0, 2.8, 5.7),
        )
        self.obstacles = self.columns + self.iconostasis + self.furniture

    def can_stand(self, x: float, z: float) -> bool:
        r = self.player_radius
        if not (-self.half_width + r <= x <= self.half_width - r):
            return False
        if not (r <= z <= self.length - r):
            return False
        return not any(box.touches_circle(x, z, r) for box in self.obstacles)


class ChurchNavigator:
    def __init__(self, world: ChurchWorld) -> None:
        self.world = world
        self.camera = Camera(x=0.0, z=24.0)
        self.walk_speed = 3.0
        self.mouse_sensitivity = 0.0025
        self.jump_speed = 4.4
        self.gravity = 10.8
        self.vertical_velocity = 0.0

    def jump(self) -> None:
        if self.camera.jump_height == 0.0 and self.vertical_velocity == 0.0:
            self.vertical_velocity = self.jump_speed

    def update_vertical(self, dt: float) -> None:
        if self.vertical_velocity == 0.0 and self.camera.jump_height == 0.0:
            return
        self.vertical_velocity -= self.gravity * dt
        self.camera.jump_height += self.vertical_velocity * dt
        if self.camera.jump_height <= 0.0:
            self.camera.jump_height = 0.0
            self.vertical_velocity = 0.0

    def look(self, relative_x: float, relative_y: float) -> None:
        self.camera.yaw = (self.camera.yaw + relative_x * self.mouse_sensitivity) % (2 * math.pi)
        self.camera.pitch = max(-1.2, min(1.2, self.camera.pitch - relative_y * self.mouse_sensitivity))

    def move(self, dt: float, forward: float, strafe: float, sprint: bool = False) -> None:
        magnitude = math.hypot(forward, strafe)
        if magnitude > 1:
            forward /= magnitude
            strafe /= magnitude
        speed = self.walk_speed * (1.65 if sprint else 1.0)
        yaw = self.camera.yaw
        dx = (math.sin(yaw) * forward + math.cos(yaw) * strafe) * speed * dt
        dz = (-math.cos(yaw) * forward + math.sin(yaw) * strafe) * speed * dt
        # Separate axes to slide along walls instead of sticking to them.
        next_x = self.camera.x + dx
        if self.world.can_stand(next_x, self.camera.z):
            self.camera.x = next_x
        next_z = self.camera.z + dz
        if self.world.can_stand(self.camera.x, next_z):
            self.camera.z = next_z
