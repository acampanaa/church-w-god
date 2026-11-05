"""Build the horror church as GPU triangles with explicit materials and light."""

import math

import pygame

from .church_world import ChurchWorld
from .config import Settings
from .graphics import GpuScene, MeshBuilder
from .navigation import Camera


def _textures() -> dict[str, pygame.Surface]:
    stone = pygame.Surface((64, 64))
    stone.fill((66, 66, 65))
    for row in range(4):
        offset = 0 if row % 2 == 0 else 16
        for col in range(-1, 3):
            shade = (row * 7 + col * 11) % 18
            pygame.draw.rect(stone, (87 + shade, 86 + shade, 81 + shade),
                             (col * 32 + offset + 2, row * 16 + 2, 29, 13))
    floor = pygame.Surface((64, 64))
    floor.fill((39, 39, 41))
    for row in range(4):
        for col in range(4):
            shade = 63 if (row + col) % 2 else 75
            pygame.draw.rect(floor, (shade, shade - 2, shade - 4),
                             (col * 16 + 1, row * 16 + 1, 14, 14))
    plaster = pygame.Surface((64, 64))
    plaster.fill((81, 82, 79))
    for y in range(0, 64, 8):
        for x in range(0, 64, 8):
            shade = (x * 3 + y * 5) % 13
            pygame.draw.rect(plaster, (87 + shade, 87 + shade, 82 + shade),
                             (x, y, 7, 7))
    for x0, y0, x1, y1 in ((6, 7, 13, 20), (38, 4, 29, 28), (48, 40, 55, 63)):
        pygame.draw.line(plaster, (49, 51, 51), (x0, y0), (x1, y1), 1)
    wood = pygame.Surface((64, 64))
    wood.fill((43, 26, 24))
    for x in range(0, 64, 4):
        shade = (x * 9) % 17
        pygame.draw.line(wood, (59 + shade, 34 + shade // 3, 29), (x, 0), (x, 63), 2)
    return {"stone": stone, "floor": floor, "plaster": plaster, "wood": wood}


def _icon(mesh: MeshBuilder, x: float, z: float) -> None:
    mesh.quad(((x - .57, .75, z), (x + .57, .75, z),
               (x + .57, 3.05, z), (x - .57, 3.05, z)), color=(.60, .39, .13))
    mesh.quad(((x - .48, .84, z + .006), (x + .48, .84, z + .006),
               (x + .48, 2.96, z + .006), (x - .48, 2.96, z + .006)),
              color=(.19, .25, .30))
    mesh.disc(x, 2.30, z + .012, .35, color=(.78, .57, .20))
    mesh.triangle(((x, 1.88, z + .018), (x - .44, .94, z + .018),
                   (x + .44, .94, z + .018)), color=(.36, .16, .15))
    mesh.disc(x, 2.27, z + .024, .19, color=(.65, .42, .28))


def _cross(mesh: MeshBuilder, x: float, y: float, z: float, size: float) -> None:
    gold = (.88, .68, .26)
    mesh.quad(((x - size * .1, y - size, z), (x + size * .1, y - size, z),
               (x + size * .1, y + size, z), (x - size * .1, y + size, z)), color=gold)
    mesh.quad(((x - size * .6, y + size * .2, z + .002),
               (x + size * .6, y + size * .2, z + .002),
               (x + size * .6, y + size * .38, z + .002),
               (x - size * .6, y + size * .38, z + .002)), color=gold)


def _build(world: ChurchWorld) -> MeshBuilder:
    mesh = MeshBuilder()
    w, length = world.half_width, world.length
    for x in range(-7, 7):
        for z in range(26):
            mesh.quad(((x, 0, z), (x + 1, 0, z),
                       (x + 1, 0, z + 1), (x, 0, z + 1)), "floor")
    mesh.quad(((-w, 0, 0), (w, 0, 0), (w, 4.2, 0), (-w, 4.2, 0)), "plaster", uv=(7, 3))
    mesh.quad(((w, 0, length), (-w, 0, length), (-w, 4.2, length),
               (w, 4.2, length)), "plaster", uv=(7, 3))
    mesh.quad(((-w, 0, length), (-w, 0, 0), (-w, 4.2, 0),
               (-w, 4.2, length)), "plaster", uv=(13, 3))
    mesh.quad(((w, 0, 0), (w, 0, length), (w, 4.2, length),
               (w, 4.2, 0)), "plaster", uv=(13, 3))
    roof = ((-w, 4.2), (-4.5, 5.25), (0, 6.2), (4.5, 5.25), (w, 4.2))
    for (x0, y0), (x1, y1) in zip(roof, roof[1:]):
        mesh.quad(((x0, y0, length), (x1, y1, length),
                   (x1, y1, 0), (x0, y0, 0)), "plaster", uv=(2, 13))
    for column in world.columns:
        mesh.box(column.left, 0, column.front, column.right, 5.05,
                 column.back, "stone")
        mesh.box(column.left - .12, 4.82, column.front - .12,
                 column.right + .12, 5.18, column.back + .12, "stone")
        mesh.box(column.left - .1, 0, column.front - .1,
                 column.right + .1, .32, column.back + .1, "stone")
    for panel in world.iconostasis:
        mesh.box(panel.left, 0, panel.front, panel.right, 3.4, panel.back, "wood")
        mesh.box(panel.left, 3.4, panel.front - .08,
                 panel.right, 3.72, panel.back + .08, "wood")
    mesh.box(-1.25, 3.1, 3.65, 1.25, 3.72, 3.95, "wood")
    altar = world.furniture[0]
    mesh.box(altar.left, 0, altar.front, altar.right, 1.05, altar.back, "wood")
    mesh.quad(((-1.05, .015, 4), (1.05, .015, 4),
               (1.05, .015, 25), (-1.05, .015, 25)), color=(.22, .035, .04))
    for x in (-1.0, 1.0):
        mesh.quad(((x - .025, .018, 4), (x + .025, .018, 4),
                   (x + .025, .018, 25), (x - .025, .018, 25)),
                  color=(.35, .26, .13))
    for side in (-1, 1):
        x = side * 6.982
        for center in (7.0, 12.0, 17.0, 22.0):
            for section, color in enumerate(((.07, .12, .18), (.18, .08, .11),
                                             (.31, .08, .07))):
                z = center - .63 + section * .42
                mesh.quad(((x, 1.45, z), (x, 1.45, z + .41),
                           (x, 3.55, z + .41), (x, 3.55, z)), color=color)
    for x in (-5.4, -3.65, -2.05, 2.05, 3.65, 5.4):
        _icon(mesh, x, 3.98)
    _cross(mesh, 0, 3.74, 4.0, .45)
    _cross(mesh, 0, 2.6, .04, .75)
    for stand in world.furniture[1:]:
        mesh.box(stand.left, 0, stand.front, stand.right, 1, stand.back, "wood")
        mesh.box(stand.left - .15, 1, stand.front - .15,
                 stand.right + .15, 1.12, stand.back + .15, "wood")
        x = (stand.left + stand.right) / 2
        z = (stand.front + stand.back) / 2
        for offset in (-.22, 0, .22):
            cx = x + offset
            mesh.quad(((cx - .035, 1.12, z + .02), (cx + .035, 1.12, z + .02),
                       (cx + .035, 1.44, z + .02), (cx - .035, 1.44, z + .02)),
                      color=(.86, .75, .48))
            mesh.triangle(((cx - .055, 1.45, z + .03), (cx + .055, 1.45, z + .03),
                           (cx, 1.64, z + .03)), "flame", color=(1, .57, .12))
    return mesh


class ChurchRenderer:
    def __init__(self, settings: Settings, world: ChurchWorld):
        self.scene = GpuScene(_build(world), _textures(), settings.width, settings.height)

    def resize(self, width: int, height: int) -> None:
        self.scene.resize(width, height)

    def close(self) -> None:
        self.scene.close()

    def draw(self, world: ChurchWorld, camera: Camera, elapsed: float = 0.0) -> None:
        flicker = .90 + .06 * math.sin(elapsed * 4.1) + .04 * math.sin(elapsed * 17)
        if math.sin(elapsed * .83) > .995:
            flicker *= .55
        self.scene.draw(camera, elapsed, clear=(.025, .026, .035),
                        light_pos=(0, 3.7, 7),
                        light_color=(.97 * flicker, .64 * flicker, .40 * flicker),
                        ambient=.28, fog_start=5, fog_end=21,
                        eye_height=1.65 + camera.jump_height)
