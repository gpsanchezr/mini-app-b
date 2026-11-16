import re
import sqlite3
from collections.abc import Iterator
from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    test_database_path = tmp_path / "test_gasto_claro.db"
    original_get_connection = main.get_connection

    def get_test_connection(
        _: Path = main.DATABASE_PATH,
    ) -> AbstractContextManager[sqlite3.Connection]:
        return original_get_connection(database_path=test_database_path)

    monkeypatch.setattr(main, "get_connection", get_test_connection)

    with TestClient(main.app, follow_redirects=False) as test_client:
        yield test_client


def create_expense(
    client: TestClient,
    description: str = "Café",
    category: str = "Alimentación",
    amount: str = "45.50",
    expense_date: str = "2026-11-16",
):
    return client.post(
        "/gastos",
        data={
            "descripcion": description,
            "categoria": category,
            "monto": amount,
            "fecha": expense_date,
        },
    )


def test_home_displays_empty_expense_list(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Historial de gastos" in response.text
    assert "Tu historial empieza aquí" in response.text


def test_create_expense_and_show_category_report(client: TestClient) -> None:
    response = create_expense(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    page = client.get("/")
    assert page.status_code == 200
    assert "Café" in page.text
    assert "$ 45.50 MXN" in page.text
    assert "Gastos por categoría" in page.text


def test_filter_expenses_by_category_and_description(client: TestClient) -> None:
    create_expense(client, description="Café", category="Alimentación")
    create_expense(
        client,
        description="Autobús",
        category="Transporte",
        amount="20.00",
    )

    response = client.get("/", params={"categoria": "Alimentación", "buscar": "Café"})

    assert response.status_code == 200
    assert "Café" in response.text
    assert "Autobús" not in response.text
    assert "$ 45.50 MXN" in response.text


def test_create_expense_rejects_invalid_amount(client: TestClient) -> None:
    response = create_expense(client, amount="-10.00")

    assert response.status_code == 422


def test_delete_expense(client: TestClient) -> None:
    create_expense(client)
    page = client.get("/")
    match = re.search(r'action="/gastos/(\d+)/eliminar"', page.text)
    assert match is not None
    expense_id = match.group(1)

    response = client.post(f"/gastos/{expense_id}/eliminar")

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert 'class="expense-name">Café</span>' not in client.get("/").text


def test_delete_missing_expense_returns_not_found(client: TestClient) -> None:
    response = client.post("/gastos/999/eliminar")

    assert response.status_code == 404
