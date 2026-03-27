from app.models.user import User
from app.core.security import hash_password
from app.models.enums import users_role


def test_listar_usuarios_como_admin(client, admin_user, admin_headers):
    res = client.get("/users/", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == 1


def test_listar_usuarios_como_cliente_prohibido(client, client_user, client_headers):
    res = client.get("/users/", headers=client_headers)
    assert res.status_code == 403


def test_obtener_usuario_por_id(client, admin_user, admin_headers):
    res = client.get(f"/users/{admin_user.id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "admin@test.com"


def test_obtener_usuario_inexistente(client, admin_headers, admin_user):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/users/{fake_id}", headers=admin_headers)
    assert res.status_code == 404


def test_crear_usuario_como_admin(client, admin_user, admin_headers):
    res = client.post("/users/", json={
        "name": "Nuevo Usuario",
        "email": "nuevo@test.com",
        "password": "password123"
    }, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "nuevo@test.com"
    # El rol siempre debe ser CLIENT sin importar lo que se envíe
    assert data["role"] == users_role.CLIENT


def test_crear_usuario_rol_forzado_a_client(client, admin_user, admin_headers):
    """Aunque se envíe role=admin, el CRUD lo fuerza a CLIENT."""
    res = client.post("/users/", json={
        "name": "Intento Admin",
        "email": "hack@test.com",
        "password": "password123",
        "role": "admin"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["role"] == users_role.CLIENT


def test_crear_usuario_email_duplicado(client, admin_user, admin_headers):
    res = client.post("/users/", json={
        "name": "Duplicado",
        "email": "admin@test.com",
        "password": "password123"
    }, headers=admin_headers)
    assert res.status_code == 400


def test_crear_usuario_sin_permiso(client, client_user, client_headers):
    res = client.post("/users/", json={
        "name": "Nuevo",
        "email": "nuevo2@test.com",
        "password": "password123"
    }, headers=client_headers)
    assert res.status_code == 403


def test_actualizar_usuario(client, admin_user, admin_headers):
    res = client.patch(f"/users/{admin_user.id}", json={
        "name": "Nombre Actualizado"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Nombre Actualizado"


def test_desactivar_usuario(client, db, admin_user, admin_headers, client_user):
    res = client.delete(f"/users/{client_user.id}", headers=admin_headers)
    assert res.status_code == 204

    db.refresh(client_user)
    assert client_user.is_active is False


def test_desactivar_usuario_inexistente(client, admin_user, admin_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.delete(f"/users/{fake_id}", headers=admin_headers)
    assert res.status_code == 404
