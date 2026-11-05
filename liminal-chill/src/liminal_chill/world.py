"""Floor plan, collisions and first-person movement for the liminal space."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Rectangle:
    left: float
    front: float
    right: float
    back: float

    def touches_circle(self, x: float, z: float, radius: float) -> bool:
        near_x = max(self.left, min(x, self.right))
        near_z = max(self.front, min(z, self.back))
        return (x - near_x) ** 2 + (z - near_z) ** 2 < radius ** 2


@dataclass
class Camera:
    x: float = 0.0
    z: float = 29.0
    yaw: float = 0.0
    pitch: float = 0.0
    jump_height: float = 0.0


class LiminalWorld:
    half_width = 9.0
    length = 32.0
    player_radius = 0.28

    def __init__(self) -> None:
        self.partitions = tuple(
            Rectangle(left, z - 0.18, right, z + 0.18)
            for z in (10.0, 22.0)
            for left, right in ((-9.0, -2.8), (2.8, 9.0))
        )
        self.pool = Rectangle(-3.5, 12.5, 3.5, 19.5)
        self.columns = tuple(
            Rectangle(x - 0.42, z - 0.42, x + 0.42, z + 0.42)
            for x in (-6.8, 6.8)
            for z in (5.0, 16.0, 27.0)
        )
        self.obstacles = self.partitions + (self.pool,) + self.columns

    def can_stand(self, x: float, z: float) -> bool:
        radius = self.player_radius
        if not (-self.half_width + radius <= x <= self.half_width - radius):
            return False
        if not (radius <= z <= self.length - radius):
            return False
        return not any(box.touches_circle(x, z, radius) for box in self.obstacles)


class Navigator:
    def __init__(self, world: LiminalWorld) -> None:
        self.world = world
        self.camera = Camera()
        self.walk_speed = 2.7
        self.mouse_sensitivity = 0.0025
        self.jump_speed = 4.2
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
        self.camera.pitch = max(-1.1, min(1.1, self.camera.pitch - relative_y * self.mouse_sensitivity))

    def move(self, dt: float, forward: float, strafe: float, faster: bool = False) -> None:
        magnitude = math.hypot(forward, strafe)
        if magnitude > 1:
            forward /= magnitude
            strafe /= magnitude
        speed = self.walk_speed * (1.5 if faster else 1.0)
        yaw = self.camera.yaw
        dx = (math.sin(yaw) * forward + math.cos(yaw) * strafe) * speed * dt
        dz = (-math.cos(yaw) * forward + math.sin(yaw) * strafe) * speed * dt
        if self.world.can_stand(self.camera.x + dx, self.camera.z):
            self.camera.x += dx
        if self.world.can_stand(self.camera.x, self.camera.z + dz):
            self.camera.z += dz
