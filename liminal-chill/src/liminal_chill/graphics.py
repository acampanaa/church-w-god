"""Explicit mesh buffers, GLSL shaders, textures and matrix uniforms."""

from array import array
import ctypes
import math

import pygame
from . import gl_compat  # noqa: F401  # Configure PyOpenGL before GL imports.
from OpenGL.GL import (
    GL_ARRAY_BUFFER, GL_COLOR_BUFFER_BIT, GL_COMPILE_STATUS,
    GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FALSE, GL_FLOAT, GL_FRAGMENT_SHADER,
    GL_LINK_STATUS, GL_NEAREST, GL_REPEAT, GL_RGB, GL_STATIC_DRAW, GL_TEXTURE0,
    GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_TRIANGLES, GL_UNSIGNED_BYTE,
    GL_VERTEX_SHADER, glActiveTexture, glAttachShader, glBindBuffer,
    glBindTexture, glBindVertexArray, glBufferData, glClear, glClearColor,
    glCompileShader, glCreateProgram, glCreateShader, glDeleteBuffers,
    glDeleteProgram, glDeleteShader, glDeleteTextures, glDeleteVertexArrays,
    glDrawArrays, glEnable, glEnableVertexAttribArray, glGenBuffers,
    glGenTextures, glGenVertexArrays, glGetProgramInfoLog, glGetProgramiv,
    glGetShaderInfoLog, glGetShaderiv, glGetUniformLocation, glLinkProgram,
    glShaderSource, glTexImage2D, glTexParameteri, glUniform1f, glUniform1i,
    glUniform3f, glUniformMatrix4fv, glUseProgram, glVertexAttribPointer,
    glViewport,
)

from . import math3d


VERTEX_SHADER = """#version 330 core
layout(location=0) in vec3 a_position;
layout(location=1) in vec2 a_uv;
layout(location=2) in vec3 a_color;
layout(location=3) in vec3 a_normal;
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
out vec2 v_uv;
out vec3 v_color;
out vec3 v_normal;
out vec3 v_world;
out float v_distance;
void main() {
    vec4 world = u_model * vec4(a_position, 1.0);
    vec4 eye = u_view * world;
    gl_Position = u_projection * eye;
    v_uv = a_uv;
    v_color = a_color;
    v_normal = mat3(u_model) * a_normal;
    v_world = world.xyz;
    v_distance = length(eye.xyz);
}
"""

FRAGMENT_SHADER = """#version 330 core
in vec2 v_uv;
in vec3 v_color;
in vec3 v_normal;
in vec3 v_world;
in float v_distance;
out vec4 frag_color;
uniform sampler2D u_texture;
uniform int u_material;
uniform vec3 u_light_pos;
uniform vec3 u_light_color;
uniform vec3 u_fog_color;
uniform float u_fog_start;
uniform float u_fog_end;
uniform float u_ambient;
uniform float u_time;
void main() {
    vec3 base = v_color;
    if (u_material == 1) base *= texture(u_texture, v_uv).rgb;
    if (u_material == 2) {
        float wave = sin(v_world.x * 2.7 + u_time * 1.3) *
                     sin(v_world.z * 2.1 - u_time * 0.8);
        base *= 0.94 + 0.08 * wave;
    }
    if (u_material == 3) base *= 0.88 + 0.12 * sin(u_time * 13.0 + v_world.x * 5.0);
    vec3 normal = normalize(v_normal);
    vec3 to_light = u_light_pos - v_world;
    float distance2 = dot(to_light, to_light);
    float diffuse = abs(dot(normal, normalize(to_light)));
    float strength = u_ambient + diffuse * 2.4 / (1.0 + 0.035 * distance2);
    vec3 lit = base * (vec3(u_ambient) + u_light_color *
                        max(0.0, strength - u_ambient));
    if (u_material == 3) lit = base;
    float fog = clamp((v_distance - u_fog_start) /
                      max(0.01, u_fog_end - u_fog_start), 0.0, 1.0);
    frag_color = vec4(mix(lit, u_fog_color, fog), 1.0);
}
"""


class MeshBuilder:
    """Build triangles with interleaved position, UV, color and normal floats."""

    def __init__(self):
        self.batches: dict[str, list[float]] = {}

    def triangle(self, vertices, material="solid", color=(1.0, 1.0, 1.0), uv=None):
        if uv is None:
            uv = ((0, 0), (1, 0), (0, 1))
        a, b, c = vertices
        ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        normal = (ab[1] * ac[2] - ab[2] * ac[1],
                  ab[2] * ac[0] - ab[0] * ac[2],
                  ab[0] * ac[1] - ab[1] * ac[0])
        length = math.sqrt(sum(component * component for component in normal)) or 1.0
        normal = tuple(component / length for component in normal)
        batch = self.batches.setdefault(material, [])
        for point, tex in zip(vertices, uv):
            batch.extend((*point, *tex, *color, *normal))

    def quad(self, vertices, material="solid", color=(1.0, 1.0, 1.0), uv=(1.0, 1.0)):
        u, v = uv
        tex = ((0, 0), (u, 0), (u, v), (0, v))
        self.triangle((vertices[0], vertices[1], vertices[2]), material, color, tex[:3])
        self.triangle((vertices[0], vertices[2], vertices[3]), material, color,
                      (tex[0], tex[2], tex[3]))

    def box(self, x0, y0, z0, x1, y1, z1, material="solid", color=(1, 1, 1)):
        faces = (
            ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)),
            ((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)),
            ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)),
            ((x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)),
            ((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)),
            ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
        )
        for face in faces:
            self.quad(face, material, color)

    def disc(self, x, y, z, radius, material="solid", color=(1, 1, 1)):
        for step in range(12):
            a = step * math.pi / 6
            b = (step + 1) * math.pi / 6
            self.triangle(((x, y, z),
                           (x + math.cos(a) * radius, y + math.sin(a) * radius, z),
                           (x + math.cos(b) * radius, y + math.sin(b) * radius, z)),
                          material, color)


def _shader(kind, source):
    shader = glCreateShader(kind)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        log = glGetShaderInfoLog(shader)
        raise RuntimeError(log.decode("utf-8", "replace") if isinstance(log, bytes) else str(log))
    return shader


class GpuScene:
    """Own one VAO, one VBO, a shader program and material textures."""

    def __init__(self, mesh: MeshBuilder, surfaces: dict[str, pygame.Surface], width: int, height: int):
        vertex = _shader(GL_VERTEX_SHADER, VERTEX_SHADER)
        fragment = _shader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER)
        self.program = glCreateProgram()
        glAttachShader(self.program, vertex)
        glAttachShader(self.program, fragment)
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            log = glGetProgramInfoLog(self.program)
            raise RuntimeError(log.decode("utf-8", "replace") if isinstance(log, bytes) else str(log))
        glDeleteShader(vertex)
        glDeleteShader(fragment)
        glUseProgram(self.program)
        self.uniform = {name: glGetUniformLocation(self.program, name) for name in (
            "u_model", "u_view", "u_projection", "u_texture", "u_material",
            "u_light_pos", "u_light_color", "u_fog_color", "u_fog_start",
            "u_fog_end", "u_ambient", "u_time",
        )}
        glUniform1i(self.uniform["u_texture"], 0)
        glEnable(GL_DEPTH_TEST)

        data = array("f")
        self.ranges = []
        for material, values in mesh.batches.items():
            start = len(data) // 11
            data.extend(values)
            self.ranges.append((material, start, len(values) // 11))
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        payload = data.tobytes()
        glBufferData(GL_ARRAY_BUFFER, len(payload), payload, GL_STATIC_DRAW)
        stride = 11 * 4
        for index, size, offset in ((0, 3, 0), (1, 2, 12), (2, 3, 20), (3, 3, 32)):
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glBindVertexArray(0)

        self.textures = {}
        for name, surface in surfaces.items():
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface.get_width(),
                         surface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE,
                         pygame.image.tostring(surface, "RGB", True))
            self.textures[name] = texture
        self.resize(width, height)

    def resize(self, width: int, height: int):
        self.width, self.height = max(1, width), max(1, height)
        glViewport(0, 0, self.width, self.height)

    def _matrix(self, name, matrix):
        glUniformMatrix4fv(self.uniform[name], 1, GL_FALSE,
                           (ctypes.c_float * 16)(*math3d.column_major(matrix)))

    def draw(self, camera, elapsed, clear, light_pos, light_color,
             ambient, fog_start, fog_end, eye_height=1.65):
        glClearColor(clear[0], clear[1], clear[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)
        glBindVertexArray(self.vao)
        self._matrix("u_model", math3d.identity())
        self._matrix("u_view", math3d.view(camera.x, eye_height, camera.z,
                                          camera.yaw, camera.pitch))
        self._matrix("u_projection", math3d.perspective(
            72.0, self.width / self.height, 0.05, 65.0))
        glUniform3f(self.uniform["u_light_pos"], *light_pos)
        glUniform3f(self.uniform["u_light_color"], *light_color)
        glUniform3f(self.uniform["u_fog_color"], *clear)
        glUniform1f(self.uniform["u_fog_start"], fog_start)
        glUniform1f(self.uniform["u_fog_end"], fog_end)
        glUniform1f(self.uniform["u_ambient"], ambient)
        glUniform1f(self.uniform["u_time"], elapsed)
        glActiveTexture(GL_TEXTURE0)
        for material, start, count in self.ranges:
            kind = {"solid": 0, "water": 2, "flame": 3}.get(material, 1)
            glUniform1i(self.uniform["u_material"], kind)
            movement = (0.012 * math.sin(elapsed * 1.3) if kind == 2 else
                        0.025 * math.sin(elapsed * 13) if kind == 3 else 0.0)
            self._matrix("u_model", math3d.translation(0, movement, 0))
            if kind == 1:
                glBindTexture(GL_TEXTURE_2D, self.textures[material])
            glDrawArrays(GL_TRIANGLES, start, count)
        glBindVertexArray(0)

    def close(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])
        if self.textures:
            glDeleteTextures(len(self.textures), list(self.textures.values()))
        glDeleteProgram(self.program)
