# Hallway 95

Un punto de partida inspirado en **3D Maze** de Windows 95, hecho con Python, Pygame y PyOpenGL. Por ahora incluye un laberinto aleatorio, paredes de ladrillo, piso y techo texturizados, una cámara con recorrido automático y exploración manual.

## Ejecutar

Requiere Python 3.10 o posterior y una computadora con OpenGL compatible con el perfil clásico.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m hallway95
```

Para repetir el mismo laberinto: `python -m hallway95 --seed 95`.

La prueba de generación se ejecuta con `python -m unittest discover -s tests`.

El proyecto desactiva `OpenGL_accelerate`, que es opcional, para evitar fallos cuando esa extensión instalada no coincide con PyOpenGL. No hace falta reinstalar el proyecto tras modificar archivos en una instalación editable (`pip install -e .`).

## Controles

| Tecla | Acción |
| --- | --- |
| Espacio | Alternar recorrido automático y manual |
| W / S o flechas arriba / abajo | Avanzar / retroceder en modo manual |
| A / D | Desplazarse lateralmente en modo manual |
| Flechas izquierda / derecha | Girar en modo manual |
| R | Crear otro laberinto |
| Esc | Salir |

## Estructura

- `maze.py`: generación y datos del laberinto, sin dependencias gráficas.
- `navigation.py`: cámara, recorrido automático y movimiento manual.
- `renderer.py`: texturas y dibujo con OpenGL clásico.
- `app.py`: ventana, eventos y bucle de Pygame.
- `config.py`: valores ajustables del prototipo.

El renderizador usa la API fija de OpenGL para mantener el aspecto de la época y facilitar el primer prototipo. El modelo del laberinto y la navegación están separados para permitir cambiar el renderizador más adelante.
