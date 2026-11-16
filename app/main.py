from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, StringConstraints

from app import servicios

BASE_DIR = Path(__file__).resolve().parent.parent
CATEGORIAS = ("comida", "transporte", "estudio", "otros")

Descripcion = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
]
Categoria = Literal["comida", "transporte", "estudio", "otros"]


class GastoEntrada(BaseModel):
    descripcion: Descripcion
    valor: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    categoria: Categoria


app = FastAPI(title="Registro de gastos")
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
def pagina_principal(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"categorias": CATEGORIAS},
    )


@app.post("/api/gastos", status_code=201)
def crear_gasto(gasto: GastoEntrada) -> dict[str, int | str | float]:
    return servicios.crear_gasto(
        descripcion=gasto.descripcion,
        valor=gasto.valor,
        categoria=gasto.categoria,
    )


@app.get("/api/gastos")
def listar_gastos() -> list[dict[str, int | str | float]]:
    return servicios.listar_gastos()


@app.get("/api/gastos/resumen")
def obtener_resumen() -> dict[str, int | dict[str, int | float]]:
    return servicios.obtener_resumen()
