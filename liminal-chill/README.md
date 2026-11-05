# Liminal Chill

Un espacio liminal tranquilo y recorrible con estética 3D noventera: tres salas conectadas, columnas repetidas, baldosas claras, paneles luminosos y un estanque turquesa. No hay enemigos ni objetivos; la primera versión se centra en pasear y observar el ambiente.

## Instalar y ejecutar

Desde PowerShell, con Python 3.10 o posterior y un controlador compatible con **OpenGL 3.3 Core**:

```powershell
cd C:\projects\church-w-god\liminal-chill
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m liminal_chill
```

## Controles

| Entrada | Acción |
| --- | --- |
| W / A / S / D | Caminar |
| Ratón o flechas | Mirar |
| Espacio | Saltar |
| Mayús | Caminar más rápido |
| Tab | Soltar o capturar el ratón |
| Clic izquierdo | Volver a capturar el ratón |
| R | Volver al inicio |
| Esc | Salir |

## Organización

- `src/liminal_chill/world.py`: planta, colisiones y movimiento.
- `src/liminal_chill/renderer.py`: geometría, texturas y agua.
- `src/liminal_chill/graphics.py`: shaders GLSL, VAO, VBO y subida de texturas.
- `src/liminal_chill/math3d.py`: matrices de modelo, vista y proyección.
- `src/liminal_chill/app.py`: ventana y controles.
- `tests/`: pruebas de la planta y las colisiones.

Ejecuta las pruebas con `python -m unittest discover -s tests -v`. Este proyecto se instala y ejecuta sin el paquete de la iglesia. La escena usa OpenGL 3.3 Core: crea triángulos y texturas en Python, carga vértices en un VBO, configura un VAO y dibuja con shaders GLSL. El shader aplica iluminación, niebla y movimiento al agua; `math3d.py` calcula las matrices de modelo, vista y proyección.

La barra de título muestra los FPS aproximados para registrar mediciones durante la futura comparación con Three.js.
