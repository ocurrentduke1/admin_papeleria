from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

# crear producto
def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# obtener producto por id
def get_product(db: Session, product_id: str):
    return db.query(Product).filter(Product.id == product_id).first()

# obtener todos los productos
def get_products(db: Session):
    return db.query(Product).all()

# actualizar producto
def update_product(db: Session, product: Product, data: ProductUpdate):
    for field, value, in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

# eliminar producto
def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()