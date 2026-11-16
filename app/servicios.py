from threading import Lock

CATEGORIAS = ("comida", "transporte", "estudio", "otros")
Gasto = dict[str, int | str | float]

_gastos: list[Gasto] = []
_siguiente_id = 1
_bloqueo = Lock()


def crear_gasto(descripcion: str, valor: float, categoria: str) -> Gasto:
    global _siguiente_id

    with _bloqueo:
        gasto: Gasto = {
            "id": _siguiente_id,
            "descripcion": descripcion,
            "valor": valor,
            "categoria": categoria,
        }
        _gastos.append(gasto)
        _siguiente_id += 1
    return gasto.copy()


def listar_gastos() -> list[Gasto]:
    with _bloqueo:
        return [gasto.copy() for gasto in _gastos]


def eliminar_gasto(gasto_id: int) -> bool:
    with _bloqueo:
        for indice, gasto in enumerate(_gastos):
            if gasto["id"] == gasto_id:
                del _gastos[indice]
                return True
    return False


def obtener_resumen() -> dict[str, int | float | dict[str, int | float]]:
    with _bloqueo:
        por_categoria: dict[str, int | float] = dict.fromkeys(CATEGORIAS, 0)
        for gasto in _gastos:
            categoria = str(gasto["categoria"])
            por_categoria[categoria] += float(gasto["valor"])

    return {
        "total": sum(por_categoria.values()),
        "por_categoria": por_categoria,
    }
