"""Pygame window, events and the main loop for both scenes."""

import argparse

import pygame

from .config import Settings
from .church_renderer import ChurchRenderer
from .church_world import ChurchNavigator, ChurchWorld
from .maze import Maze
from .navigation import Navigator
from .renderer import Renderer


def main() -> None:
    parser = argparse.ArgumentParser(description="A 90s-style horror church")
    parser.add_argument("--maze", action="store_true", help="Open the original maze prototype")
    parser.add_argument("--seed", type=int, help="Generate a repeatable maze with --maze")
    args = parser.parse_args()
    settings = Settings()
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    if not args.maze:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                        pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.set_mode(
        (settings.width, settings.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    )
    if args.maze:
        maze = Maze.generate(settings.maze_width, settings.maze_height, args.seed)
        navigator = Navigator(maze, settings)
        renderer = Renderer(settings)
        pygame.display.set_caption("Church Horror | Laberinto | Espacio: modo  R: nuevo  Esc: salir")
    else:
        world = ChurchWorld()
        navigator = ChurchNavigator(world)
        renderer = ChurchRenderer(settings, world)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        pygame.mouse.get_rel()
        pygame.display.set_caption("Church Horror | WASD: mover  Espacio: saltar  Tab: cursor  Esc: salir")
    clock = pygame.time.Clock()
    last_fps_update = 0
    running = True
    try:
        while running:
            dt = min(clock.tick(settings.fps) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    renderer.resize(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif args.maze and event.key == pygame.K_SPACE:
                        navigator.toggle_auto()
                    elif not args.maze and event.key == pygame.K_SPACE:
                        navigator.jump()
                    elif event.key == pygame.K_r:
                        if args.maze:
                            maze = Maze.generate(settings.maze_width, settings.maze_height)
                            navigator = Navigator(maze, settings)
                        else:
                            navigator = ChurchNavigator(world)
                    elif not args.maze and event.key == pygame.K_TAB:
                        grabbed = not pygame.event.get_grab()
                        pygame.event.set_grab(grabbed)
                        pygame.mouse.set_visible(not grabbed)
                        pygame.mouse.get_rel()
                elif not args.maze and event.type == pygame.MOUSEMOTION and pygame.event.get_grab():
                    navigator.look(*event.rel)
                elif not args.maze and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)
                    pygame.mouse.get_rel()
            keys = pygame.key.get_pressed()
            if args.maze:
                if navigator.auto:
                    navigator.update_auto(dt)
                else:
                    forward = int(keys[pygame.K_w] or keys[pygame.K_UP]) - int(keys[pygame.K_s] or keys[pygame.K_DOWN])
                    strafe = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
                    turn = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
                    navigator.update_manual(dt, forward, strafe, turn)
                renderer.draw(maze, navigator.camera)
            else:
                forward = int(keys[pygame.K_w]) - int(keys[pygame.K_s])
                strafe = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
                sprint = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                navigator.move(dt, forward, strafe, sprint)
                navigator.update_vertical(dt)
                arrow_x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
                arrow_y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
                navigator.look(arrow_x * 400 * dt, arrow_y * 400 * dt)
                renderer.draw(world, navigator.camera, pygame.time.get_ticks() / 1000.0)
            pygame.display.flip()
            now = pygame.time.get_ticks()
            if now - last_fps_update >= 500:
                label = "Church Horror | Laberinto" if args.maze else "Church Horror | Iglesia"
                pygame.display.set_caption(f"{label} | {clock.get_fps():.0f} FPS | Esc: salir")
                last_fps_update = now
    finally:
        if not args.maze:
            renderer.close()
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()
