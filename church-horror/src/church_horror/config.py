from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    width: int = 960
    height: int = 600
    fps: int = 60
    maze_width: int = 13
    maze_height: int = 13
    eye_height: float = 0.5
    walk_speed: float = 2.4
    turn_speed: float = 2.0
    auto_step_seconds: float = 0.85
    auto_turn_seconds: float = 0.45
