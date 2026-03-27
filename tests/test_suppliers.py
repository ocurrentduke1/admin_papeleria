SUPPLIER_DATA = {
    "name": "Distribuidora XYZ",
    "contact_name": "Maria Lopez",
    "email": "xyz@distribuidora.com",
    "phone": "555-1234",
}


def test_listar_proveedores_autenticado(client, admin_user, admin_headers):
    res = client.get("/suppliers/", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_listar_proveedores_sin_token(client):
    res = client.get("/suppliers/")
    assert res.status_code == 401


def test_crear_proveedor_como_admin(client, admin_user, admin_headers):
    res = client.post("/suppliers/", json=SUPPLIER_DATA, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == SUPPLIER_DATA["email"]
    assert data["name"] == SUPPLIER_DATA["name"]


def test_crear_proveedor_como_cliente_prohibido(client, client_user, client_headers):
    res = client.post("/suppliers/", json=SUPPLIER_DATA, headers=client_headers)
    assert res.status_code == 403


def test_crear_proveedor_como_empleado_prohibido(client, employee_user, employee_headers):
    res = client.post("/suppliers/", json=SUPPLIER_DATA, headers=employee_headers)
    assert res.status_code == 403


def test_obtener_proveedor_por_id(client, supplier, admin_headers, admin_user):
    res = client.get(f"/suppliers/{supplier.id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["email"] == supplier.email


def test_obtener_proveedor_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/suppliers/{fake_id}", headers=admin_headers)
    assert res.status_code == 404


def test_actualizar_proveedor(client, supplier, admin_user, admin_headers):
    res = client.patch(f"/suppliers/{supplier.id}", json={
        "name": "Nombre Actualizado"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Nombre Actualizado"


def test_desactivar_proveedor(client, db, supplier, admin_user, admin_headers):
    res = client.delete(f"/suppliers/{supplier.id}", headers=admin_headers)
    assert res.status_code == 204

    db.refresh(supplier)
    assert supplier.is_active is False


def test_desactivar_proveedor_sin_permiso(client, supplier, client_user, client_headers):
    res = client.delete(f"/suppliers/{supplier.id}", headers=client_headers)
    assert res.status_code == 403
