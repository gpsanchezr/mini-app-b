# Gasto Claro Versión B

Aplicación web en español para registrar, filtrar, eliminar y consultar gastos por categoría. Los datos se guardan en la base de datos local `gasto_claro.db` con SQLite.

## Requisitos

- Python 3.10 o posterior

## Instalación y ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Abre <http://127.0.0.1:8000>. La base de datos se crea automáticamente al iniciar la aplicación.

Puedes cambiar la moneda mostrada editando `format_currency` en `main.py`; actualmente los importes se etiquetan como MXN.

## Pruebas y lint

Instala las dependencias de desarrollo y ejecuta las comprobaciones:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
ruff check
```
