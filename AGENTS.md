# AGENTS.md

## Proyecto
Mini-aplicación de práctica: Registro de gastos. Datos ficticios en memoria, sin base de datos.

## Stack
Python 3.14, FastAPI y plantillas Jinja2
pytest con TestClient, Ruff

## Comandos
Instalar: pip install -r requirements.txt
Ejecutar: uvicorn app.main:app --reload
Pruebas: python -m pytest -v
Estilo: uff check .

## Estructura
pp/main.py: crea la aplicación y define las rutas
pp/servicios.py: lógica y datos en memoria, sin FastAPI
pp/templates/index.html: página principal con HTML, CSS y JavaScript
	ests/test_aceptacion.py: contrato de la API; no se modifica

## Qué no hacer
No modificar ni borrar tests/test_aceptacion.py.
No instalar dependencias que no estén en requirements.txt.
No usar base de datos ni archivos para guardar datos.
No hacer commit ni push.

## Lecciones aprendidas
Cada vez que el agente se equivoque, se escribe aquí la regla que evita repetir el error.
