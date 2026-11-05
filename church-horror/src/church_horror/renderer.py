"""OpenGL compatibility renderer, isolated from maze and navigation logic."""

import math

import pygame
from . import gl_compat  # noqa: F401  # Must run before OpenGL.GL is imported.

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FOG,
    GL_FOG_COLOR, GL_FOG_END, GL_FOG_MODE, GL_FOG_START, GL_LINEAR,
    GL_MODELVIEW, GL_PROJECTION, GL_QUADS,
    GL_REPEAT, GL_RGB, GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
    GL_UNPACK_ALIGNMENT, GL_UNSIGNED_BYTE, glBegin, glBindTexture,
    glClear, glClearColor, glColor3f, glEnable, glEnd, glFogf, glFogfv,
    glFogi, glGenTextures, glLoadIdentity, glMatrixMode, glPixelStorei,
    glRotatef, glTexCoord2f, glTexImage2D, glTexParameteri, glTranslatef,
    glVertex3f, glViewport,
)
from OpenGL.GLU import gluPerspective

from .config import Settings
from .maze import EAST, NORTH, SOUTH, WEST, Maze
from .navigation import Camera


def _make_textures() -> list[pygame.Surface]:
    brick = pygame.Surface((128, 128))
    brick.fill((96, 40, 38))
    for row in range(8):
        offset = 0 if row % 2 == 0 else 16
        for col in range(-1, 5):
            left = col * 32 + offset + 2
            top = row * 16 + 2
            tone = ((col * 11 + row * 7) % 4) * 5
            pygame.draw.rect(brick, (147 + tone, 69 + tone // 2, 55), (left, top, 29, 13))
            pygame.draw.line(brick, (171 + tone, 92, 70), (left, top), (left + 28, top))

    floor = pygame.Surface((128, 128))
    floor.fill((69, 67, 63))
    for y in range(0, 128, 32):
        for x in range(0, 128, 32):
            shade = 82 if (x // 32 + y // 32) % 2 else 73
            pygame.draw.rect(floor, (shade, shade - 2, shade - 5), (x + 2, y + 2, 29, 29))

    ceiling = pygame.Surface((128, 128))
    ceiling.fill((87, 87, 76))
    for y in range(0, 128, 32):
        for x in range(0, 128, 32):
            pygame.draw.rect(ceiling, (108, 108, 96), (x + 2, y + 2, 29, 29))
            pygame.draw.rect(ceiling, (75, 75, 66), (x + 2, y + 2, 29, 29), 1)
    return [brick, floor, ceiling]


class Renderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.textures = []
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.08, 0.07, 0.07, 1.0)
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, (0.08, 0.07, 0.07, 1.0))
        glFogf(GL_FOG_START, 3.0)
        glFogf(GL_FOG_END, 11.0)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        for surface in _make_textures():
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            pixels = pygame.image.tostring(surface, "RGB", True)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface.get_width(), surface.get_height(),
                         0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
            self.textures.append(texture)
        self.resize(settings.width, settings.height)

    def resize(self, width: int, height: int) -> None:
        glViewport(0, 0, width, max(1, height))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(75.0, width / max(1, height), 0.05, 40.0)
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def _quad(vertices: tuple[tuple[float, float, float], ...]) -> None:
        glBegin(GL_QUADS)
        for (u, v), (x, y, z) in zip(((0, 0), (1, 0), (1, 1), (0, 1)), vertices):
            glTexCoord2f(u, v)
            glVertex3f(x, y, z)
        glEnd()

    def draw(self, maze: Maze, camera: Camera) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glRotatef(math.degrees(camera.yaw), 0, 1, 0)
        glColor3f(1, 1, 1)
        # Eye height is half a tile; the world is translated beneath it.
        glTranslatef(-camera.x, -self.settings.eye_height, -camera.z)

        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        for z in range(maze.height):
            for x in range(maze.width):
                self._quad(((x, 0, z), (x + 1, 0, z),
                            (x + 1, 0, z + 1), (x, 0, z + 1)))

        glBindTexture(GL_TEXTURE_2D, self.textures[2])
        for z in range(maze.height):
            for x in range(maze.width):
                self._quad(((x, 1, z + 1), (x + 1, 1, z + 1),
                            (x + 1, 1, z), (x, 1, z)))

        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        for z in range(maze.height):
            for x in range(maze.width):
                if maze.has_wall(x, z, NORTH):
                    self._quad(((x + 1, 0, z), (x, 0, z), (x, 1, z), (x + 1, 1, z)))
                if maze.has_wall(x, z, WEST):
                    self._quad(((x, 0, z), (x, 0, z + 1), (x, 1, z + 1), (x, 1, z)))
                if x == maze.width - 1 and maze.has_wall(x, z, EAST):
                    self._quad(((x + 1, 0, z + 1), (x + 1, 0, z),
                                (x + 1, 1, z), (x + 1, 1, z + 1)))
                if z == maze.height - 1 and maze.has_wall(x, z, SOUTH):
                    self._quad(((x, 0, z + 1), (x + 1, 0, z + 1),
                                (x + 1, 1, z + 1), (x, 1, z + 1)))
