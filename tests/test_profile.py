def test_obtener_mi_perfil(client, client_user, client_headers):
    res = client.get("/users/me", headers=client_headers)
    assert res.status_code == 200
    assert res.json()["email"] == client_user.email


def test_actualizar_mi_nombre(client, client_user, client_headers):
    res = client.patch("/users/me", json={"name": "Nombre Nuevo"}, headers=client_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Nombre Nuevo"


def test_actualizar_mi_email(client, client_user, client_headers):
    res = client.patch("/users/me", json={"email": "nuevo@email.com"}, headers=client_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "nuevo@email.com"


def test_actualizar_perfil_sin_token(client):
    res = client.patch("/users/me", json={"name": "X"})
    assert res.status_code == 401


def test_cambiar_password_correcta(client, client_user, client_headers):
    res = client.post("/users/me/change-password", json={
        "current_password": "cliente1234",
        "new_password": "nueva_password123"
    }, headers=client_headers)
    assert res.status_code == 204


def test_cambiar_password_incorrecta(client, client_user, client_headers):
    res = client.post("/users/me/change-password", json={
        "current_password": "wrongpassword",
        "new_password": "nueva_password123"
    }, headers=client_headers)
    assert res.status_code == 400


def test_cambiar_password_nueva_muy_corta(client, client_user, client_headers):
    res = client.post("/users/me/change-password", json={
        "current_password": "cliente1234",
        "new_password": "123"
    }, headers=client_headers)
    assert res.status_code == 422


def test_cambiar_password_permite_nuevo_login(client, client_user, client_headers):
    """Después de cambiar la password, el login con la nueva funciona."""
    client.post("/users/me/change-password", json={
        "current_password": "cliente1234",
        "new_password": "nueva_password123"
    }, headers=client_headers)

    res = client.post("/auth/login", json={
        "email": client_user.email,
        "password": "nueva_password123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_no_puedo_cambiar_rol_desde_mi_perfil(client, client_user, client_headers):
    """`/users/me` no acepta el campo role — solo name y email."""
    res = client.patch("/users/me", json={"role": "admin"}, headers=client_headers)
    # El campo role es ignorado por UserSelfUpdate, el status sigue siendo client
    assert res.status_code == 200
    assert res.json()["role"] == "client"
