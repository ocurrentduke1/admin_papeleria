from app.models.enums import order_status_type


def _order_payload(product_id: str, quantity: int = 2) -> dict:
    return {"items": [{"product_id": product_id, "quantity": quantity}]}


# ── Creación ─────────────────────────────────────────────────────────────────

def test_crear_orden_como_cliente(client, product, client_user, client_headers):
    res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == order_status_type.PENDING
    assert len(data["order_items"]) == 1
    assert float(data["total"]) == float(product.price * 2)


def test_crear_orden_descuenta_stock(client, db, product, client_user, client_headers):
    stock_inicial = product.stock
    client.post("/orders/", json=_order_payload(str(product.id), quantity=5), headers=client_headers)
    db.refresh(product)
    assert product.stock == stock_inicial - 5


def test_crear_orden_stock_insuficiente(client, product, client_user, client_headers):
    res = client.post("/orders/", json=_order_payload(str(product.id), quantity=9999), headers=client_headers)
    assert res.status_code == 400


def test_crear_orden_producto_inexistente(client, client_user, client_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.post("/orders/", json=_order_payload(fake_id), headers=client_headers)
    assert res.status_code == 400


def test_crear_orden_sin_token(client, product):
    res = client.post("/orders/", json=_order_payload(str(product.id)))
    assert res.status_code == 401


# ── Consulta ─────────────────────────────────────────────────────────────────

def test_listar_ordenes_como_admin(client, product, admin_user, admin_headers, client_user, client_headers):
    client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    res = client.get("/orders/", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_listar_ordenes_como_cliente_prohibido(client, client_user, client_headers):
    res = client.get("/orders/", headers=client_headers)
    assert res.status_code == 403


def test_cliente_ve_su_propia_orden(client, product, client_user, client_headers):
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    order_id = create_res.json()["id"]
    res = client.get(f"/orders/{order_id}", headers=client_headers)
    assert res.status_code == 200


def test_cliente_no_ve_orden_ajena(client, db, product, admin_user, admin_headers, client_user, client_headers):
    """El cliente no puede ver una orden que pertenece a otro usuario."""
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=admin_headers)
    order_id = create_res.json()["id"]
    res = client.get(f"/orders/{order_id}", headers=client_headers)
    assert res.status_code == 403


def test_obtener_orden_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/orders/{fake_id}", headers=admin_headers)
    assert res.status_code == 404


# ── Actualización de estado ───────────────────────────────────────────────────

def test_actualizar_estado_orden(client, product, admin_user, admin_headers, client_user, client_headers):
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    order_id = create_res.json()["id"]

    res = client.patch(f"/orders/{order_id}", json={"status": "confirmed"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == order_status_type.CONFIRMED


def test_transicion_estado_invalida(client, product, admin_user, admin_headers, client_user, client_headers):
    """No se puede saltar de PENDING a DELIVERED directamente."""
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    order_id = create_res.json()["id"]

    res = client.patch(f"/orders/{order_id}", json={"status": "delivered"}, headers=admin_headers)
    assert res.status_code == 400


def test_actualizar_estado_como_cliente_prohibido(client, product, client_user, client_headers):
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    order_id = create_res.json()["id"]

    res = client.patch(f"/orders/{order_id}", json={"status": "confirmed"}, headers=client_headers)
    assert res.status_code == 403


# ── Cancelación ───────────────────────────────────────────────────────────────

def test_cancelar_orden_pendiente(client, db, product, admin_user, admin_headers, client_user, client_headers):
    stock_inicial = product.stock
    create_res = client.post("/orders/", json=_order_payload(str(product.id), quantity=3), headers=client_headers)
    order_id = create_res.json()["id"]

    res = client.delete(f"/orders/{order_id}", headers=client_headers)
    assert res.status_code == 200
    assert res.json()["status"] == order_status_type.CANCELLED

    # El stock debe haberse restaurado
    db.refresh(product)
    assert product.stock == stock_inicial


def test_cancelar_orden_no_pendiente(client, product, admin_user, admin_headers, client_user, client_headers):
    """No se puede cancelar una orden ya confirmada."""
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=client_headers)
    order_id = create_res.json()["id"]

    # Confirmar la orden primero
    client.patch(f"/orders/{order_id}", json={"status": "confirmed"}, headers=admin_headers)

    res = client.delete(f"/orders/{order_id}", headers=client_headers)
    assert res.status_code == 400


def test_cliente_no_cancela_orden_ajena(client, product, admin_user, admin_headers, client_user, client_headers):
    create_res = client.post("/orders/", json=_order_payload(str(product.id)), headers=admin_headers)
    order_id = create_res.json()["id"]

    res = client.delete(f"/orders/{order_id}", headers=client_headers)
    assert res.status_code == 403
