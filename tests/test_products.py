def _product_payload(supplier_id: str, sku: str = "LAP-001") -> dict:
    return {
        "name": "Lapicero Azul",
        "sku": sku,
        "price": 1.50,
        "stock": 100,
        "stock_min": 10,
        "supplier_id": supplier_id,
    }


def test_listar_productos(client, admin_user, admin_headers):
    res = client.get("/products/", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_listar_productos_sin_token(client):
    res = client.get("/products/")
    assert res.status_code == 401


def test_crear_producto_como_admin(client, supplier, admin_user, admin_headers):
    res = client.post("/products/", json=_product_payload(str(supplier.id)), headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["sku"] == "LAP-001"
    assert data["stock"] == 100


def test_crear_producto_como_empleado(client, supplier, employee_user, employee_headers):
    res = client.post("/products/", json=_product_payload(str(supplier.id)), headers=employee_headers)
    assert res.status_code == 201


def test_crear_producto_como_cliente_prohibido(client, supplier, client_user, client_headers):
    res = client.post("/products/", json=_product_payload(str(supplier.id)), headers=client_headers)
    assert res.status_code == 403


def test_crear_producto_proveedor_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.post("/products/", json=_product_payload(fake_id), headers=admin_headers)
    assert res.status_code == 400


def test_crear_producto_sku_duplicado(client, product, supplier, admin_user, admin_headers):
    res = client.post("/products/", json=_product_payload(str(supplier.id), sku="LAP-001"), headers=admin_headers)
    assert res.status_code == 400


def test_obtener_producto_por_id(client, product, admin_user, admin_headers):
    res = client.get(f"/products/{product.id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["sku"] == product.sku


def test_obtener_producto_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/products/{fake_id}", headers=admin_headers)
    assert res.status_code == 404


def test_actualizar_producto(client, product, admin_user, admin_headers):
    res = client.patch(f"/products/{product.id}", json={
        "price": 2.99,
        "stock": 200
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert float(data["price"]) == 2.99
    assert data["stock"] == 200


def test_actualizar_producto_sin_permiso(client, product, client_user, client_headers):
    res = client.patch(f"/products/{product.id}", json={"price": 9.99}, headers=client_headers)
    assert res.status_code == 403


def test_eliminar_producto_como_admin(client, product, admin_user, admin_headers):
    res = client.delete(f"/products/{product.id}", headers=admin_headers)
    assert res.status_code == 204


def test_eliminar_producto_como_empleado_prohibido(client, product, employee_user, employee_headers):
    res = client.delete(f"/products/{product.id}", headers=employee_headers)
    assert res.status_code == 403
