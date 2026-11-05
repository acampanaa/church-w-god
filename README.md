# Dos proyectos de exploración 3D

Este repositorio contiene dos aplicaciones independientes hechas con **Python, Pygame y PyOpenGL**:

| Proyecto | Ambiente | Inicio |
| --- | --- | --- |
| [church-horror](church-horror/README.md) | Iglesia oscura de inspiración ortodoxa | `python -m church_horror` |
| [liminal-chill](liminal-chill/README.md) | Espacio liminal tranquilo con salas pastel y estanque | `python -m liminal_chill` |

Cada carpeta tiene su propio `pyproject.toml`, paquete `src`, pruebas y README. Las escenas principales usan OpenGL 3.3 Core con shaders, VBO, VAO y matrices explícitas. Instala cada una desde su carpeta con `python -m pip install -e .`, preferiblemente en un entorno virtual propio. Los comandos completos están en los README de cada proyecto.

La instalación editable anterior de `hallway95` en la raíz ya no corresponde a esta estructura; instala los nuevos paquetes antes de ejecutarlos.
