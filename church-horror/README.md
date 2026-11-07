# Church Horror

Exploración libre de una iglesia oscura, con estética 3D de los años 90. La escena principal incluye una nave, columnas, vitrales apagados, iconostasio, iconos geométricos, cruz, candelabros y luz inestable. El antiguo laberinto permanece como prototipo opcional.

También puedes iniciarla desde el [menú principal](../README.md) con `python menu.py` en la raíz del repositorio.

## Instalar y ejecutar

Desde PowerShell, con Python 3.10 o posterior y un controlador compatible con **OpenGL 3.3 Core**:

```powershell
cd C:\projects\church-w-god\church-horror
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m church_horror
```

Después de instalar en modo editable, basta con `python -m church_horror` para ver cambios de código. Para el laberinto anterior usa `python -m church_horror --maze`; puedes fijar su generación con `--seed 95`.

## Controles de la iglesia

| Entrada | Acción |
| --- | --- |
| W / A / S / D | Caminar |
| Ratón o flechas | Mirar |
| Espacio | Saltar |
| Mayús | Caminar más rápido |
| Tab | Soltar o capturar el ratón |
| Clic izquierdo | Volver a capturar el ratón |
| R | Volver a la entrada |
| Esc | Salir |

En el laberinto opcional, `Espacio` conserva su función de alternar recorrido automático y manual, y `R` genera otro laberinto.

## Organización

- `src/church_horror/church_world.py`: planta, obstáculos y movimiento.
- `src/church_horror/church_renderer.py`: materiales, geometría y atmósfera.
- `src/church_horror/graphics.py`: shaders GLSL, VAO, VBO y subida de texturas.
- `src/church_horror/math3d.py`: matrices de modelo, vista y proyección.
- `src/church_horror/app.py`: ventana, eventos y selección de escena.
- `src/church_horror/maze.py`, `navigation.py`, `renderer.py`: laberinto anterior.
- `tests/`: pruebas de lógica y colisiones.

Ejecuta las pruebas con `python -m unittest discover -s tests -v`. La escena principal usa OpenGL 3.3 Core: genera triángulos en Python, los carga en un VBO, define sus atributos en un VAO y los dibuja con shaders GLSL. Las matrices 4×4 se calculan en `math3d.py` y se envían como uniformes. El shader aplica textura, iluminación puntual, niebla y animación de las llamas. El laberinto opcional conserva el renderizador clásico para comparar técnicas.

La barra de título muestra los FPS aproximados para registrar mediciones durante la futura comparación con Three.js.

La extensión opcional `OpenGL_accelerate` está desactivada para evitar incompatibilidades con instalaciones existentes.
