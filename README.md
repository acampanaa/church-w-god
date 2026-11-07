# Dos proyectos de exploración 3D

Este repositorio contiene dos aplicaciones independientes hechas con **Python, Pygame y PyOpenGL**:

| Proyecto | Ambiente | Inicio |
| --- | --- | --- |
| [church-horror](church-horror/README.md) | Iglesia oscura de inspiración ortodoxa | `python -m church_horror` |
| [liminal-chill](liminal-chill/README.md) | Espacio liminal tranquilo con salas pastel y estanque | `python -m liminal_chill` |

## Menú principal

Desde la raíz del repositorio puedes abrir un menú pixelado que reúne ambas experiencias:

```powershell
cd C:\projects\church-w-god
python -m pip install -r requirements.txt
python menu.py
```

Usa las flechas o las teclas `1` y `2` para elegir, y `Enter` o un clic para iniciar. `Esc` cierra el menú. Al salir de una experiencia vuelves al menú. El menú usa el mismo intérprete de Python y abre cada proyecto en un proceso independiente; no hace falta instalar los paquetes en modo editable para usarlo.

Cada carpeta tiene su propio `pyproject.toml`, paquete `src`, pruebas y README. Las escenas principales usan OpenGL 3.3 Core con shaders, VBO, VAO y matrices explícitas. También puedes instalar cada proyecto desde su carpeta con `python -m pip install -e .` y ejecutarlo por separado. Los comandos completos están en sus README.

La instalación editable anterior de `hallway95` en la raíz ya no corresponde a esta estructura.
