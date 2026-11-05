"""Small row-major 4x4 matrix module, independent of OpenGL."""

import math


def identity() -> tuple[float, ...]:
    return (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)


def multiply(a, b) -> tuple[float, ...]:
    return tuple(sum(a[row * 4 + k] * b[k * 4 + col] for k in range(4))
                 for row in range(4) for col in range(4))


def translation(x: float, y: float, z: float) -> tuple[float, ...]:
    return (1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z, 0, 0, 0, 1)


def rotation_x(angle: float) -> tuple[float, ...]:
    c, s = math.cos(angle), math.sin(angle)
    return (1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1)


def rotation_y(angle: float) -> tuple[float, ...]:
    c, s = math.cos(angle), math.sin(angle)
    return (c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1)


def perspective(fov_degrees: float, aspect: float, near: float, far: float) -> tuple[float, ...]:
    f = 1 / math.tan(math.radians(fov_degrees) / 2)
    return (f / aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far + near) / (near - far), 2 * far * near / (near - far),
            0, 0, -1, 0)


def view(x: float, eye_y: float, z: float, yaw: float, pitch: float) -> tuple[float, ...]:
    return multiply(multiply(rotation_x(-pitch), rotation_y(yaw)),
                    translation(-x, -eye_y, -z))


def column_major(matrix) -> tuple[float, ...]:
    return tuple(matrix[row * 4 + col] for col in range(4) for row in range(4))
