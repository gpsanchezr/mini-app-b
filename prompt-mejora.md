## Rol
Actúa como desarrollador backend con experiencia en FastAPI, Jinja2 y pruebas con pytest.

## Objetivo
Agregar la funcionalidad para eliminar gastos en la mini-aplicación de Registro de gastos:
1. Crear el endpoint DELETE /api/gastos/{id} que elimine el gasto y responda con el código 204; si el gasto no existe, responda con el código 404.
2. Asegurar que el resumen del sistema deje de contar el gasto eliminado.
3. Actualizar la interfaz principal para incluir un botón funcional en cada gasto que permita eliminarlo de manera asíncrona.
4. Crear una prueba nueva en tests/test_mejora.py que compruebe explícitamente esta mejora.

## Contexto
Lee AGENTS.md y los archivos en app/main.py y app/servicios.py. El contrato de aceptación existente en tests/test_aceptacion.py no debe modificarse bajo ninguna circunstancia.

## Restricciones
- No modifiques ni borres tests/test_aceptacion.py.
- Usa solo las dependencias declaradas en requirements.txt.
- Mantén la persistencia y la arquitectura modular actual.

## Formato de salida
Antes de escribir código, muestra el plan con las rutas completas de los archivos que vas a modificar o crear (incluyendo tests/test_mejora.py) y espera mi aprobación.

## Ejemplo
- DELETE /api/gastos/1 elimina el gasto con ID 1 y responde con estado HTTP 204.
- Intentar eliminar un ID inexistente (DELETE /api/gastos/9999) responde con estado HTTP 404.

## Criterio de éxito
python -m pytest -v pasa todas las pruebas (incluyendo tests/test_mejora.py) y ruff check . no reporta errores. Si después de 3 intentos las pruebas no pasan, detente y explica el problema.
