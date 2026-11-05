"""Pygame entry point for the calm liminal scene."""

import pygame

from .renderer import Renderer
from .world import LiminalWorld, Navigator


def main() -> None:
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                    pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.set_mode((960, 600), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption("Liminal Chill | WASD: mover  Espacio: saltar  Tab: cursor  Esc: salir")
    world = LiminalWorld()
    navigator = Navigator(world)
    renderer = Renderer(world)
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.mouse.get_rel()
    clock = pygame.time.Clock()
    last_fps_update = 0
    running = True
    try:
        while running:
            dt = min(clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    renderer.resize(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        navigator.jump()
                    elif event.key == pygame.K_r:
                        navigator = Navigator(world)
                    elif event.key == pygame.K_TAB:
                        grabbed = not pygame.event.get_grab()
                        pygame.event.set_grab(grabbed)
                        pygame.mouse.set_visible(not grabbed)
                        pygame.mouse.get_rel()
                elif event.type == pygame.MOUSEMOTION and pygame.event.get_grab():
                    navigator.look(*event.rel)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)
                    pygame.mouse.get_rel()
            keys = pygame.key.get_pressed()
            forward = int(keys[pygame.K_w]) - int(keys[pygame.K_s])
            strafe = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            faster = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            navigator.move(dt, forward, strafe, faster)
            navigator.update_vertical(dt)
            arrow_x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            arrow_y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            navigator.look(arrow_x * 400 * dt, arrow_y * 400 * dt)
            renderer.draw(world, navigator.camera, pygame.time.get_ticks() / 1000.0)
            pygame.display.flip()
            now = pygame.time.get_ticks()
            if now - last_fps_update >= 500:
                pygame.display.set_caption(
                    f"Liminal Chill | {clock.get_fps():.0f} FPS | Esc: salir"
                )
                last_fps_update = now
    finally:
        renderer.close()
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()
