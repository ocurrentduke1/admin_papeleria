import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.api.deps import get_db
from app.core.database import Base
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.enums import users_role

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Usuarios ────────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    user = User(
        name="Admin Test",
        email="admin@test.com",
        password_hash=hash_password("admin1234"),
        role=users_role.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def employee_user(db):
    user = User(
        name="Empleado Test",
        email="empleado@test.com",
        password_hash=hash_password("empleado1234"),
        role=users_role.EMPLOYEE,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client_user(db):
    user = User(
        name="Cliente Test",
        email="cliente@test.com",
        password_hash=hash_password("cliente1234"),
        role=users_role.CLIENT,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Tokens y headers ────────────────────────────────────────────────────────

@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_headers(employee_user):
    token = create_access_token({"sub": str(employee_user.id), "role": employee_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers(client_user):
    token = create_access_token({"sub": str(client_user.id), "role": client_user.role})
    return {"Authorization": f"Bearer {token}"}


# ── Datos de dominio ─────────────────────────────────────────────────────────

@pytest.fixture
def supplier(db):
    s = Supplier(
        name="Proveedor Test",
        contact_name="Juan Perez",
        email="proveedor@test.com",
        is_active=True,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def product(db, supplier):
    p = Product(
        name="Lapicero Azul",
        sku="LAP-001",
        price=1.50,
        stock=100,
        stock_min=10,
        supplier_id=supplier.id,
        is_active=True,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
