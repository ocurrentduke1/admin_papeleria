from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.product import Product
from app.models.inventory_movement import InventoryMovement
from app.schemas.order import OrderCreate, OrderUpdate
from app.models.enums import order_status_type, order_status_type as OrderStatus

# crear orden
def create_order(db: Session, order_data: OrderCreate):
    try:
        total = 0.0

        # 1️⃣ Crear la orden
        order = Order(
            user_id=order_data.user_id,
            status=order_status_type.PENDING
        )
        db.add(order)
        db.flush()  # obtiene order.id sin commit

        # 2️⃣ Crear items
        for item in order_data.items:
            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .first()
            )

            if not product:
                raise ValueError(f"Producto {item.product_id} no existe")

            if product.stock < item.quantity:
                raise ValueError(
                    f"Stock insuficiente para {product.name}"
                )

            subtotal = product.price * item.quantity
            total += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(order_item)

            # 3️⃣ Descontar inventario
            product.stock -= item.quantity

            # 4️⃣ Registrar movimiento
            movement = InventoryMovement(
                product_id=product.id,
                quantity=-item.quantity,
                reason="order"
            )
            db.add(movement)

        # 5️⃣ Guardar total
        order.total_amount = total

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise

# obtener orden por id
def get_order(db: Session, order_id: str):
    return (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

# obtener todas las ordenes
def get_orders(db: Session):
    return db.query(Order).all()

# actualizar orden
def update_order(
    db: Session,
    order_id: int,
    order_data: OrderUpdate
):
    order = get_order(db, order_id)

    if not order:
        return None

    # Validar transición de estado
    if order_data.status:
        if not _is_valid_status_change(order.status, order_data.status):
            raise ValueError(
                f"No se puede cambiar de {order.status} a {order_data.status}"
            )
        order.status = order_data.status

    db.commit()
    db.refresh(order)
    return order

# eliminar orden
def cancel_order(db: Session, order_id: str):
    order = get_order(db, order_id)

    if not order:
        return None

    if order.status != order_status_type.PENDING:
        raise ValueError("Solo órdenes pendientes se pueden cancelar")

    order.status = order_status_type.CANCELLED

    for item in order.items:
        product = item.product
        product.stock += item.quantity

        movement = InventoryMovement(
            product_id=product.id,
            quantity=item.quantity,
            reason="order_cancelled"
        )
        db.add(movement)

    db.commit()
    db.refresh(order)
    return order

def _is_valid_status_change(current: OrderStatus, new: OrderStatus) -> bool:
    allowed_transitions = {
        OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELLED},
        OrderStatus.PAID: {OrderStatus.SHIPPED},
        OrderStatus.SHIPPED: set(),
        OrderStatus.CANCELLED: set(),
    }
    return new in allowed_transitions[current]
