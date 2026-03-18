import uuid
from datetime import datetime

# Importar todos los modelos para que SQLAlchemy los registre
from app.models import user, product, supplier, orders, order_items, inventory_movement

from app.core.database import sessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import users_role

def create_admin():
    db = sessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@papeleria.com").first()
        if existing:
            print("El admin ya existe")
            return

        admin = User(
            id=uuid.uuid4(),
            name="Admin",
            email="admin@papeleria.com",
            password_hash=hash_password("admin1234"),
            role=users_role.ADMIN,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(admin)
        db.commit()
        print(f"Admin creado con ID: {admin.id}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()