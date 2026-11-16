## Rol
Actúa como desarrollador backend con experiencia en FastAPI, Jinja2 y pruebas con pytest.

## Objetivo
Construir la mini-aplicación web Registro de gastos con estos requisitos:
1. GET / muestra un formulario para registrar un gasto, la lista de gastos y el total por categoría.
2. POST /api/gastos recibe {"descripcion": "Almuerzo", "valor": 15000, "categoria": "comida"} y responde con el código 201 y el gasto creado con su id.
3. Las categorías válidas son comida, transporte, estudio y otros. El valor debe ser mayor que 0 y la descripción debe tener entre 1 y 80 caracteres. Si algún dato no es válido, responde con el código 422.
4. GET /api/gastos devuelve la lista de gastos.
5. GET /api/gastos/resumen devuelve {"total": número, "por_categoria": {...}} con las cuatro categorías, aunque alguna tenga 0.

## Contexto
Lee AGENTS.md. El contrato de la API está en tests/test_aceptacion.py: las rutas, los nombres de los campos y los códigos de estado deben coincidir con esas pruebas.

## Restricciones
Usa solo las dependencias de requirements.txt.
Define las rutas en app/main.py y la lógica en app/servicios.py, sin importar FastAPI en servicios.
Guarda los datos en memoria, sin base de datos ni archivos.
No modifiques tests/test_aceptacion.py.
La página usa HTML, CSS y JavaScript sin librerías externas.

## Formato de salida
Antes de escribir código, muestra el plan con las rutas completas de los archivos que vas a crear y espera mi aprobación. Al terminar, resume en una línea qué hace cada archivo.

## Ejemplo
POST /api/gastos con {"descripcion": "Almuerzo", "valor": 15000, "categoria": "comida"} responde con el código 201 y devuelve:
{"id": 1, "descripcion": "Almuerzo", "valor": 15000, "categoria": "comida"}

GET /api/gastos/resumen devuelve:
{"total": 15000, "por_categoria": {"comida": 15000, "transporte": 0, "estudio": 0, "otros": 0}}

## Criterio de éxito
python -m pytest -v pasa todas las pruebas y ruff check no reporta errores. Si después de 3 intentos las pruebas no pasan, detente y explica el problema.
