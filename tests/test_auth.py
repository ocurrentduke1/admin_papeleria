def test_login_exitoso(client, admin_user):
    res = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "admin1234"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_password_incorrecta(client, admin_user):
    res = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "incorrecta"
    })
    assert res.status_code == 400


def test_login_email_inexistente(client):
    res = client.post("/auth/login", json={
        "email": "noexiste@test.com",
        "password": "cualquiera"
    })
    assert res.status_code == 400


def test_login_usuario_inactivo(client, db, admin_user):
    admin_user.is_active = False
    db.commit()

    res = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "admin1234"
    })
    assert res.status_code == 400


def test_ruta_protegida_sin_token(client):
    res = client.get("/users/")
    assert res.status_code == 401


def test_ruta_protegida_token_invalido(client):
    res = client.get("/users/", headers={"Authorization": "Bearer token_falso"})
    assert res.status_code == 401


# ── Registro público ──────────────────────────────────────────────────────────

def test_registro_exitoso(client):
    res = client.post("/auth/register", json={
        "name": "Nuevo Cliente",
        "email": "nuevo@test.com",
        "password": "password123"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "nuevo@test.com"
    assert data["role"] == "client"


def test_registro_rol_siempre_client(client):
    res = client.post("/auth/register", json={
        "name": "Hacker",
        "email": "hacker@test.com",
        "password": "password123",
        "role": "admin"
    })
    assert res.status_code == 201
    assert res.json()["role"] == "client"


def test_registro_email_duplicado(client):
    client.post("/auth/register", json={
        "name": "Usuario 1",
        "email": "dup@test.com",
        "password": "password123"
    })
    res = client.post("/auth/register", json={
        "name": "Usuario 2",
        "email": "dup@test.com",
        "password": "password123"
    })
    assert res.status_code == 400


def test_registro_password_corta(client):
    res = client.post("/auth/register", json={
        "name": "Usuario",
        "email": "short@test.com",
        "password": "123"
    })
    assert res.status_code == 422
