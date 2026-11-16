import sqlite3
from collections.abc import Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "gasto_claro.db"
CATEGORIES = (
    "Alimentación",
    "Transporte",
    "Vivienda",
    "Servicios",
    "Salud",
    "Ocio",
    "Educación",
    "Compras",
    "Otros",
)
MAX_AMOUNT_CENTS = 99_999_999_999


@contextmanager
def get_connection(database_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                categoria TEXT NOT NULL,
                monto_centavos INTEGER NOT NULL CHECK (monto_centavos > 0),
                fecha TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha)"
        )


def format_currency(amount_cents: int) -> str:
    whole, cents = divmod(amount_cents, 100)
    return f"$ {whole:,}.{cents:02d} MXN"


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Gasto Claro Versión B", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
def home(
    request: Request,
    categoria: Annotated[str | None, Query()] = None,
    desde: Annotated[date | None, Query()] = None,
    hasta: Annotated[date | None, Query()] = None,
    buscar: Annotated[str | None, Query(max_length=100)] = None,
):
    if categoria and categoria not in CATEGORIES:
        raise HTTPException(status_code=422, detail="La categoría seleccionada no existe.")
    if desde and hasta and desde > hasta:
        raise HTTPException(
            status_code=422, detail="La fecha inicial no puede ser posterior a la final."
        )

    conditions: list[str] = []
    parameters: list[object] = []
    if categoria:
        conditions.append("categoria = ?")
        parameters.append(categoria)
    if desde:
        conditions.append("fecha >= ?")
        parameters.append(desde.isoformat())
    if hasta:
        conditions.append("fecha <= ?")
        parameters.append(hasta.isoformat())
    if buscar and buscar.strip():
        conditions.append("descripcion LIKE ?")
        parameters.append(f"%{buscar.strip()}%")
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        gastos = connection.execute(
            f"""
            SELECT id, descripcion, categoria, monto_centavos, fecha
            FROM gastos
            {where_clause}
            ORDER BY fecha DESC, id DESC
            """,
            parameters,
        ).fetchall()
        resumen = connection.execute(
            f"""
            SELECT COUNT(*) AS cantidad,
                   COALESCE(SUM(monto_centavos), 0) AS total
            FROM gastos
            {where_clause}
            """,
            parameters,
        ).fetchone()
        categorias = connection.execute(
            f"""
            SELECT categoria, COUNT(*) AS cantidad,
                   SUM(monto_centavos) AS total
            FROM gastos
            {where_clause}
            GROUP BY categoria
            ORDER BY total DESC, categoria COLLATE NOCASE
            """,
            parameters,
        ).fetchall()

    total_centavos = resumen["total"]
    reporte = [
        {
            "categoria": fila["categoria"],
            "cantidad": fila["cantidad"],
            "total": fila["total"],
            "porcentaje": round(fila["total"] * 100 / total_centavos)
            if total_centavos
            else 0,
        }
        for fila in categorias
    ]
    promedio = round(total_centavos / resumen["cantidad"]) if resumen["cantidad"] else 0

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "gastos": gastos,
            "categorias": CATEGORIES,
            "categoria_seleccionada": categoria or "",
            "desde": desde.isoformat() if desde else "",
            "hasta": hasta.isoformat() if hasta else "",
            "buscar": buscar or "",
            "cantidad": resumen["cantidad"],
            "total_centavos": total_centavos,
            "promedio_centavos": promedio,
            "reporte": reporte,
            "format_currency": format_currency,
            "fecha_hoy": date.today().isoformat(),
        },
    )


@app.post("/gastos")
def crear_gasto(
    descripcion: Annotated[str, Form(max_length=120)],
    categoria: Annotated[str, Form()],
    monto: Annotated[str, Form()],
    fecha: Annotated[date, Form()],
):
    descripcion = descripcion.strip()
    if not descripcion:
        raise HTTPException(status_code=422, detail="La descripción es obligatoria.")
    if categoria not in CATEGORIES:
        raise HTTPException(status_code=422, detail="Selecciona una categoría válida.")
    try:
        cantidad = Decimal(monto)
        centavos_decimal = (cantidad * 100).quantize(
            Decimal(1), rounding=ROUND_HALF_UP
        )
    except InvalidOperation as error:
        raise HTTPException(status_code=422, detail="El monto no es válido.") from error
    if not cantidad.is_finite() or centavos_decimal <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor que cero.")
    if centavos_decimal > MAX_AMOUNT_CENTS:
        raise HTTPException(status_code=422, detail="El monto supera el máximo permitido.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO gastos (descripcion, categoria, monto_centavos, fecha)
            VALUES (?, ?, ?, ?)
            """,
            (descripcion, categoria, int(centavos_decimal), fecha.isoformat()),
        )
    return RedirectResponse(url="/", status_code=303)


@app.post("/gastos/{gasto_id}/eliminar")
def eliminar_gasto(gasto_id: int):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No se encontró ese gasto.")
    return RedirectResponse(url="/", status_code=303)
