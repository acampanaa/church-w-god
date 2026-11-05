"""Choose the compatible PyOpenGL wrappers before any GL imports."""

import OpenGL


# OpenGL_accelerate is optional and some installed builds are incompatible.
OpenGL.USE_ACCELERATE = False
