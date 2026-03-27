import pytest
from app.models.product import Product


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def product_bajo_stock(db, supplier):
    """Producto cuyo stock está en el mínimo (debe aparecer en low-stock)."""
    p = Product(
        name="Cuaderno",
        sku="CUA-001",
        price=3.00,
        stock=5,
        stock_min=10,   # stock < stock_min → bajo mínimo
        supplier_id=supplier.id,
        is_active=True,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ── GET /inventory/ ───────────────────────────────────────────────────────────

def test_listar_movimientos_como_admin(client, admin_user, admin_headers):
    res = client.get("/inventory/", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_listar_movimientos_como_empleado(client, employee_user, employee_headers):
    res = client.get("/inventory/", headers=employee_headers)
    assert res.status_code == 200


def test_listar_movimientos_como_cliente_prohibido(client, client_user, client_headers):
    res = client.get("/inventory/", headers=client_headers)
    assert res.status_code == 403


def test_listar_movimientos_sin_token(client):
    res = client.get("/inventory/")
    assert res.status_code == 401


def test_crear_orden_genera_movimiento(client, product, admin_user, admin_headers, client_user, client_headers):
    """Al crear una orden se debe registrar un movimiento de tipo OUT."""
    client.post("/orders/", json={"items": [{"product_id": str(product.id), "quantity": 2}]},
                headers=client_headers)

    res = client.get(f"/inventory/?product_id={product.id}", headers=admin_headers)
    movements = res.json()
    assert len(movements) == 1
    assert movements[0]["type"] == "out"
    assert movements[0]["quantity"] == -2


def test_filtrar_movimientos_por_tipo(client, product, admin_user, admin_headers, client_user, client_headers):
    client.post("/orders/", json={"items": [{"product_id": str(product.id), "quantity": 1}]},
                headers=client_headers)

    res_out = client.get("/inventory/?type=out", headers=admin_headers)
    assert all(m["type"] == "out" for m in res_out.json())

    res_in = client.get("/inventory/?type=in", headers=admin_headers)
    assert res_in.json() == []


# ── GET /inventory/product/{product_id} ──────────────────────────────────────

def test_historial_por_producto(client, product, admin_user, admin_headers, client_user, client_headers):
    client.post("/orders/", json={"items": [{"product_id": str(product.id), "quantity": 3}]},
                headers=client_headers)

    res = client.get(f"/inventory/product/{product.id}", headers=admin_headers)
    assert res.status_code == 200
    movements = res.json()
    assert len(movements) == 1
    assert movements[0]["product_id"] == str(product.id)


def test_historial_producto_sin_movimientos(client, product, admin_user, admin_headers):
    res = client.get(f"/inventory/product/{product.id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json() == []


# ── POST /inventory/adjustment ────────────────────────────────────────────────

def test_ajuste_entrada_incrementa_stock(client, db, product, admin_user, admin_headers):
    stock_inicial = product.stock
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "in",
        "quantity": 20,
        "reason": "Reposición de mercancía"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["quantity"] == 20

    db.refresh(product)
    assert product.stock == stock_inicial + 20


def test_ajuste_salida_decrementa_stock(client, db, product, admin_user, admin_headers):
    stock_inicial = product.stock
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "out",
        "quantity": 10,
        "reason": "Producto dañado"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["quantity"] == -10

    db.refresh(product)
    assert product.stock == stock_inicial - 10


def test_ajuste_tipo_adjustment(client, db, product, admin_user, admin_headers):
    stock_inicial = product.stock
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "adjustment",
        "quantity": 5,
        "reason": "Corrección de inventario físico"
    }, headers=admin_headers)
    assert res.status_code == 201
    db.refresh(product)
    assert product.stock == stock_inicial + 5


def test_ajuste_salida_stock_insuficiente(client, product, admin_user, admin_headers):
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "out",
        "quantity": 9999,
        "reason": "Intento de sacar más de lo que hay"
    }, headers=admin_headers)
    assert res.status_code == 400


def test_ajuste_producto_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.post("/inventory/adjustment", json={
        "product_id": fake_id,
        "type": "in",
        "quantity": 10,
        "reason": "Test"
    }, headers=admin_headers)
    assert res.status_code == 400


def test_ajuste_sin_razon_falla(client, product, admin_user, admin_headers):
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "in",
        "quantity": 10,
        "reason": ""
    }, headers=admin_headers)
    assert res.status_code == 422


def test_ajuste_como_cliente_prohibido(client, product, client_user, client_headers):
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "in",
        "quantity": 5,
        "reason": "Test"
    }, headers=client_headers)
    assert res.status_code == 403


def test_ajuste_empleado_puede_ajustar(client, product, employee_user, employee_headers):
    res = client.post("/inventory/adjustment", json={
        "product_id": str(product.id),
        "type": "in",
        "quantity": 5,
        "reason": "Ajuste por empleado"
    }, headers=employee_headers)
    assert res.status_code == 201


# ── GET /products/low-stock ───────────────────────────────────────────────────

def test_productos_bajo_stock(client, product_bajo_stock, admin_user, admin_headers):
    res = client.get("/products/low-stock", headers=admin_headers)
    assert res.status_code == 200
    skus = [p["sku"] for p in res.json()]
    assert "CUA-001" in skus


def test_producto_con_stock_ok_no_aparece(client, product, admin_user, admin_headers):
    """El producto del fixture base tiene stock=100, stock_min=10 → no debe aparecer."""
    res = client.get("/products/low-stock", headers=admin_headers)
    assert res.status_code == 200
    skus = [p["sku"] for p in res.json()]
    assert "LAP-001" not in skus


def test_low_stock_como_cliente_prohibido(client, client_user, client_headers):
    res = client.get("/products/low-stock", headers=client_headers)
    assert res.status_code == 403
