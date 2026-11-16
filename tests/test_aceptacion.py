import pytest
from fastapi.testclient import TestClient
from app.main import app

cliente = TestClient(app)

CATEGORIAS = {"comida", "transporte", "estudio", "otros"}


def registrar(descripcion="Almuerzo", valor=15000, categoria="comida"):
    datos = {"descripcion": descripcion, "valor": valor, "categoria": categoria}
    return cliente.post("/api/gastos", json=datos)


def test_pagina_principal():
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]


def test_registrar_gasto():
    respuesta = registrar()
    assert respuesta.status_code == 201
    gasto = respuesta.json()
    assert isinstance(gasto["id"], int)
    assert gasto["descripcion"] == "Almuerzo"
    assert gasto["valor"] == pytest.approx(15000)
    assert gasto["categoria"] == "comida"


def test_listar_incluye_el_gasto():
    gasto = registrar("Pasaje", 3000, "transporte").json()
    ids = [elemento["id"] for elemento in cliente.get("/api/gastos").json()]
    assert gasto["id"] in ids


def test_resumen_tiene_las_cuatro_categorias():
    resumen = cliente.get("/api/gastos/resumen").json()
    assert set(resumen["por_categoria"]) == CATEGORIAS


def test_resumen_suma_el_gasto():
    antes = cliente.get("/api/gastos/resumen").json()
    registrar("Bus", 8000, "transporte")
    despues = cliente.get("/api/gastos/resumen").json()
    assert despues["total"] == pytest.approx(antes["total"] + 8000)
    transporte_antes = antes["por_categoria"]["transporte"]
    assert despues["por_categoria"]["transporte"] == pytest.approx(transporte_antes + 8000)


def test_valor_invalido():
    assert registrar(valor=0).status_code == 422
    assert registrar(valor=-5).status_code == 422


def test_categoria_invalida():
    assert registrar(categoria="viajes").status_code == 422
