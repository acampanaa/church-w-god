"""Pixel-art launcher for the two independent Pygame/OpenGL experiences."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import subprocess
import sys

try:
    import pygame
except ModuleNotFoundError as exc:
    raise SystemExit("Instala las dependencias: python -m pip install -r requirements.txt") from exc


ROOT = Path(__file__).resolve().parent
BASE_SIZE = (480, 300)
WINDOW_SIZE = (960, 600)
BACKGROUND = (12, 83, 84)
INK = (27, 30, 43)
WINDOW = (190, 190, 181)
LIGHT = (245, 245, 233)
SHADOW = (74, 76, 82)


@dataclass(frozen=True)
class Experience:
    name: str
    subtitle: str
    package_dir: str
    module: str
    accent: tuple[int, int, int]


EXPERIENCES = (
    Experience("IGLESIA: TERROR", "NAVE OSCURA / MISTERIO", "church-horror",
               "church_horror", (135, 51, 65)),
    Experience("ESPACIO LIMINAL", "PASEO TRANQUILO / AGUA", "liminal-chill",
               "liminal_chill", (64, 151, 154)),
)
CARDS = (pygame.Rect(37, 91, 194, 133), pygame.Rect(249, 91, 194, 133))
CLOSE_BUTTON = pygame.Rect(431, 28, 17, 16)


@lru_cache(maxsize=16)
def _font(size: int, bold: bool = False) -> pygame.font.Font:
    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font


def _label(canvas: pygame.Surface, text: str, x: int, y: int, size: int,
           color: tuple[int, int, int] = INK, bold: bool = False) -> None:
    canvas.blit(_font(size, bold).render(text, False, color), (x, y))


def _bevel(canvas: pygame.Surface, rect: pygame.Rect, fill, raised: bool = True) -> None:
    pygame.draw.rect(canvas, fill, rect)
    top = LIGHT if raised else SHADOW
    bottom = SHADOW if raised else LIGHT
    pygame.draw.line(canvas, top, rect.topleft, (rect.right - 1, rect.top))
    pygame.draw.line(canvas, top, rect.topleft, (rect.left, rect.bottom - 1))
    pygame.draw.line(canvas, bottom, (rect.left, rect.bottom - 1),
                     (rect.right - 1, rect.bottom - 1))
    pygame.draw.line(canvas, bottom, (rect.right - 1, rect.top),
                     (rect.right - 1, rect.bottom - 1))


def _church_preview(canvas: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(canvas, (30, 28, 43), rect)
    for y in range(rect.top + 3, rect.bottom, 8):
        pygame.draw.line(canvas, (44, 39, 49), (rect.left, y), (rect.right - 1, y))
    center = rect.centerx
    pygame.draw.polygon(canvas, (68, 61, 68),
                        ((center - 54, rect.bottom - 7), (center - 46, rect.top + 21),
                         (center, rect.top + 4), (center + 46, rect.top + 21),
                         (center + 54, rect.bottom - 7)))
    pygame.draw.rect(canvas, (87, 74, 70), (center - 42, rect.top + 23, 84, 37))
    pygame.draw.rect(canvas, (43, 27, 35), (center - 12, rect.top + 33, 24, 27))
    pygame.draw.rect(canvas, (130, 48, 59), (center - 34, rect.top + 30, 12, 18))
    pygame.draw.rect(canvas, (130, 48, 59), (center + 22, rect.top + 30, 12, 18))
    pygame.draw.rect(canvas, (182, 143, 74), (center - 2, rect.top + 10, 4, 19))
    pygame.draw.rect(canvas, (182, 143, 74), (center - 8, rect.top + 16, 16, 4))
    pygame.draw.polygon(canvas, (103, 61, 52),
                        ((center - 13, rect.bottom - 1), (center - 4, rect.top + 58),
                         (center + 4, rect.top + 58), (center + 13, rect.bottom - 1)))


def _liminal_preview(canvas: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(canvas, (157, 198, 188), rect)
    pygame.draw.rect(canvas, (213, 224, 205),
                     (rect.left + 3, rect.top + 3, rect.width - 6, 34))
    pygame.draw.rect(canvas, (187, 218, 205),
                     (rect.left + 3, rect.top + 38, rect.width - 6, rect.height - 41))
    for x in range(rect.left + 4, rect.right, 12):
        pygame.draw.line(canvas, (139, 184, 178), (x, rect.top + 38),
                         (x - 11, rect.bottom - 2))
    pygame.draw.polygon(canvas, (62, 146, 159),
                        ((rect.left + 35, rect.bottom - 3),
                         (rect.right - 35, rect.bottom - 3),
                         (rect.right - 53, rect.top + 44),
                         (rect.left + 53, rect.top + 44)))
    pygame.draw.rect(canvas, (248, 244, 211),
                     (rect.centerx - 28, rect.top + 9, 56, 8))
    for x in (rect.left + 16, rect.right - 22):
        pygame.draw.rect(canvas, (128, 181, 174), (x, rect.top + 12, 6, 46))


def _draw(canvas: pygame.Surface, selected: int, status: str, ticks: int) -> None:
    canvas.fill(BACKGROUND)
    for x in range(0, BASE_SIZE[0], 12):
        for y in range(0, BASE_SIZE[1], 12):
            pygame.draw.rect(canvas, (15, 91, 91), (x, y, 1, 1))

    window = pygame.Rect(20, 20, 440, 257)
    _bevel(canvas, window, WINDOW)
    pygame.draw.rect(canvas, (31, 46, 108), (25, 25, 430, 22))
    pygame.draw.rect(canvas, (63, 89, 157), (25, 25, 430, 1))
    _label(canvas, "EXPERIENCIAS 3D", 35, 28, 20, LIGHT, True)
    _bevel(canvas, CLOSE_BUTTON, WINDOW)
    _label(canvas, "x", 436, 28, 17, INK, True)
    _label(canvas, "ELIGE TU DESTINO", 34, 56, 28, INK, True)
    _label(canvas, "DOS MUNDOS / UNA MAQUINA", 35, 77, 14, SHADOW)

    for index, (experience, card) in enumerate(zip(EXPERIENCES, CARDS)):
        active = index == selected
        _bevel(canvas, card, (218, 218, 208) if active else (177, 179, 174), active)
        pygame.draw.rect(canvas, experience.accent, (card.x + 6, card.y + 6, 4, 105))
        preview = pygame.Rect(card.x + 13, card.y + 9, card.width - 21, 68)
        if index == 0:
            _church_preview(canvas, preview)
        else:
            _liminal_preview(canvas, preview)
        _label(canvas, experience.name, card.x + 13, card.y + 82, 19, INK, True)
        _label(canvas, experience.subtitle, card.x + 13, card.y + 101, 13, SHADOW)
        if active:
            _label(canvas, ">", card.right - 15, card.y + 82, 19,
                   experience.accent, True)

    pulse = (ticks // 450) % 2 == 0
    _label(canvas, "ENTER PARA INICIAR" if pulse else "ENTER PARA INICIAR_",
           34, 235, 18, INK, True)
    _label(canvas, "FLECHAS / RATON / 1-2", 34, 255, 14, SHADOW)
    _label(canvas, "ESC SALIR", 379, 255, 14, SHADOW)
    if status:
        pygame.draw.rect(canvas, (12, 83, 84), (20, 279, 440, 18))
        _label(canvas, status[:58], 24, 281, 14, LIGHT)


def _viewport(window_size: tuple[int, int]) -> tuple[pygame.Rect, float]:
    width, height = window_size
    scale = min(width / BASE_SIZE[0], height / BASE_SIZE[1])
    if scale >= 1:
        scale = float(max(1, int(scale)))
    scaled = (max(1, round(BASE_SIZE[0] * scale)),
              max(1, round(BASE_SIZE[1] * scale)))
    return pygame.Rect((width - scaled[0]) // 2, (height - scaled[1]) // 2,
                       *scaled), scale


def _mouse_to_canvas(position, viewport: pygame.Rect, scale: float):
    if not viewport.collidepoint(position):
        return None
    return (int((position[0] - viewport.x) / scale),
            int((position[1] - viewport.y) / scale))


def _launch(experience: Experience) -> str:
    project = ROOT / experience.package_dir
    source = project / "src"
    if not (source / experience.module).is_dir():
        return "NO SE ENCONTRO EL PROYECTO"
    environment = os.environ.copy()
    previous = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(source) + (os.pathsep + previous if previous else "")
    pygame.quit()
    try:
        result = subprocess.run([sys.executable, "-m", experience.module],
                                cwd=project, env=environment, check=False)
    except OSError as exc:
        return f"ERROR AL INICIAR: {exc.strerror or exc}"
    finally:
        pygame.init()
        _font.cache_clear()
    if result.returncode:
        return f"LA EXPERIENCIA TERMINO CON ERROR ({result.returncode})"
    return "HAS VUELTO AL MENU"


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("EXPERIENCIAS 3D - MENU 95")
    canvas = pygame.Surface(BASE_SIZE)
    clock = pygame.time.Clock()
    selected = 0
    status = ""
    running = True
    try:
        while running:
            viewport, scale = _viewport(screen.get_size())
            launch = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a):
                        selected = (selected - 1) % len(EXPERIENCES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d):
                        selected = (selected + 1) % len(EXPERIENCES)
                    elif event.key in (pygame.K_1, pygame.K_2):
                        selected = event.key - pygame.K_1
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        launch = True
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    point = _mouse_to_canvas(event.pos, viewport, scale)
                    if point:
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                                and CLOSE_BUTTON.collidepoint(point)):
                            running = False
                            continue
                        for index, card in enumerate(CARDS):
                            if card.collidepoint(point):
                                selected = index
                                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                    launch = True
                                break
            if not running:
                break
            if launch:
                status = _launch(EXPERIENCES[selected])
                screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
                pygame.display.set_caption("EXPERIENCIAS 3D - MENU 95")
                clock = pygame.time.Clock()
            _draw(canvas, selected, status, pygame.time.get_ticks())
            screen.fill((5, 40, 42))
            viewport, _ = _viewport(screen.get_size())
            screen.blit(pygame.transform.scale(canvas, viewport.size), viewport.topleft)
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
