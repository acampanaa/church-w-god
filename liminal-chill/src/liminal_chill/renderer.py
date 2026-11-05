"""Build a pastel liminal interior with GPU buffers and animated water shader."""

import math

import pygame

from .graphics import GpuScene, MeshBuilder
from .world import Camera, LiminalWorld


def _textures() -> dict[str, pygame.Surface]:
    tile = pygame.Surface((64, 64))
    tile.fill((163, 191, 186))
    for row in range(4):
        for col in range(4):
            tone = 4 if (row + col) % 2 else 0
            pygame.draw.rect(tile, (211 - tone, 218 - tone, 199 - tone),
                             (col * 16 + 1, row * 16 + 1, 14, 14))
    wall = pygame.Surface((64, 64))
    wall.fill((199, 210, 191))
    for y in range(0, 64, 16):
        pygame.draw.line(wall, (181, 197, 182), (0, y), (63, y), 1)
    for x in range(0, 64, 16):
        pygame.draw.line(wall, (188, 201, 184), (x, 0), (x, 63), 1)
    trim = pygame.Surface((64, 64))
    trim.fill((132, 184, 179))
    for y in range(0, 64, 8):
        pygame.draw.line(trim, (154, 200, 191), (0, y), (63, y), 2)
    return {"tile": tile, "wall": wall, "trim": trim}


def _build(world: LiminalWorld) -> MeshBuilder:
    mesh = MeshBuilder()
    for x in range(-9, 9):
        for z in range(32):
            mesh.quad(((x, 0, z), (x + 1, 0, z),
                       (x + 1, 0, z + 1), (x, 0, z + 1)), "tile")
    mesh.quad(((-9, 0, 0), (9, 0, 0), (9, 4.2, 0), (-9, 4.2, 0)),
              "wall", uv=(9, 2))
    mesh.quad(((9, 0, 32), (-9, 0, 32), (-9, 4.2, 32), (9, 4.2, 32)),
              "wall", uv=(9, 2))
    mesh.quad(((-9, 0, 32), (-9, 0, 0), (-9, 4.2, 0), (-9, 4.2, 32)),
              "wall", uv=(16, 2))
    mesh.quad(((9, 0, 0), (9, 0, 32), (9, 4.2, 32), (9, 4.2, 0)),
              "wall", uv=(16, 2))
    mesh.quad(((-9, 4.2, 32), (9, 4.2, 32), (9, 4.2, 0), (-9, 4.2, 0)),
              "wall", uv=(9, 16))
    for wall in world.partitions:
        mesh.box(wall.left, 0, wall.front, wall.right, 4.2, wall.back, "wall")
    for z in (10.0, 22.0):
        mesh.box(-2.8, 3.15, z - .18, 2.8, 4.2, z + .18, "wall")
    for column in world.columns:
        mesh.box(column.left, 0, column.front, column.right, 4.2,
                 column.back, "trim")
        mesh.box(column.left - .1, 0, column.front - .1,
                 column.right + .1, .3, column.back + .1, "trim")
    pool = world.pool
    mesh.box(pool.left, 0, pool.front, pool.right, .28, pool.front + .18, "trim")
    mesh.box(pool.left, 0, pool.back - .18, pool.right, .28, pool.back, "trim")
    mesh.box(pool.left, 0, pool.front, pool.left + .18, .28, pool.back, "trim")
    mesh.box(pool.right - .18, 0, pool.front, pool.right, .28, pool.back, "trim")
    mesh.quad(((pool.left + .18, .09, pool.front + .18),
               (pool.right - .18, .09, pool.front + .18),
               (pool.right - .18, .09, pool.back - .18),
               (pool.left + .18, .09, pool.back - .18)),
              "water", (.29, .66, .68))
    for z in (5.0, 16.0, 27.0):
        for x in (-4.0, 0.0, 4.0):
            mesh.quad(((x - 1.35, 4.19, z - .55), (x + 1.35, 4.19, z - .55),
                       (x + 1.35, 4.19, z + .55), (x - 1.35, 4.19, z + .55)),
                      color=(.95, .96, .82))
    for z in (.02, 31.98):
        mesh.quad(((-3, 1, z), (3, 1, z), (3, 3.3, z), (-3, 3.3, z)),
                  color=(.58, .78, .76))
    return mesh


class Renderer:
    def __init__(self, world: LiminalWorld, width: int = 960, height: int = 600):
        self.scene = GpuScene(_build(world), _textures(), width, height)

    def resize(self, width: int, height: int) -> None:
        self.scene.resize(width, height)

    def close(self) -> None:
        self.scene.close()

    def draw(self, world: LiminalWorld, camera: Camera, elapsed: float) -> None:
        pulse = .98 + .02 * math.sin(elapsed * .35)
        self.scene.draw(camera, elapsed, clear=(.67, .76, .73),
                        light_pos=(0, 3.8, 16),
                        light_color=(.85 * pulse, .96 * pulse, .90 * pulse),
                        ambient=.78, fog_start=16, fog_end=42,
                        eye_height=1.65 + camera.jump_height)
