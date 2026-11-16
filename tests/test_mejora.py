import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def cliente() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_eliminar_gasto_actualiza_listado_y_resumen(cliente: TestClient) -> None:
    resumen_inicial = cliente.get("/api/gastos/resumen").json()
    respuesta_creacion = cliente.post(
        "/api/gastos",
        json={"descripcion": "Gasto por eliminar", "valor": 123.45, "categoria": "comida"},
    )
    gasto_id = respuesta_creacion.json()["id"]

    respuesta_eliminacion = cliente.delete(f"/api/gastos/{gasto_id}")

    assert respuesta_eliminacion.status_code == 204
    assert respuesta_eliminacion.content == b""
    assert all(
        gasto["id"] != gasto_id
        for gasto in cliente.get("/api/gastos").json()
    )
    resumen_final = cliente.get("/api/gastos/resumen").json()
    assert resumen_final["total"] == pytest.approx(resumen_inicial["total"])
    assert resumen_final["por_categoria"]["comida"] == pytest.approx(
        resumen_inicial["por_categoria"]["comida"]
    )
    assert cliente.delete(f"/api/gastos/{gasto_id}").status_code == 404


def test_interfaz_incluye_eliminacion_asincrona(cliente: TestClient) -> None:
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "botonEliminar.textContent = \"Eliminar\"" in respuesta.text
    assert 'method: "DELETE"' in respuesta.text
