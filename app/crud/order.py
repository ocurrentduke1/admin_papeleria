from uuid import UUID
from sqlalchemy.orm import Session
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.product import Product
from app.models.inventory_movement import InventoryMovement
from app.schemas.order import OrderCreate, OrderUpdate
from app.models.enums import order_status_type, order_status_type as OrderStatus, movements_type

# crear orden
def create_order(db: Session, order_data: OrderCreate, user_id: UUID):
    try:
        total = 0

        # 1️⃣ Crear la orden
        order = Order(
            user_id=user_id,
            status=order_status_type.PENDING,
            total = 0
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
                raise ValueError(f"Product {item.product_id} does not exist")

            if product.stock < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}"
                )

            subtotal = product.price * item.quantity
            total += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=subtotal
            )
            db.add(order_item)

            # 3️⃣ Descontar inventario
            product.stock -= item.quantity

            # 4️⃣ Registrar movimiento
            movement = InventoryMovement(
                product_id=product.id,
                type=movements_type.OUT,
                quantity=-item.quantity,
                reason="order",
                created_by=user_id
            )
            db.add(movement)

        # 5️⃣ Guardar total
        order.total = total

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise

# obtener orden por id
def get_order(db: Session, order_id: UUID):
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
    order_id: UUID,
    order_data: OrderUpdate
):
    order = get_order(db, order_id)

    if not order:
        return None

    # Validar transición de estado
    if order_data.status:
        if not _is_valid_status_change(order.status, order_data.status):
            raise ValueError(
                f"Invalid status change from {order.status} to {order_data.status}"
            )
        order.status = order_data.status

    db.commit()
    db.refresh(order)
    return order

# eliminar orden
def cancel_order(db: Session, order_id: UUID, cancelled_by: UUID):
    order = get_order(db, order_id)

    if not order:
        return None

    if order.status != order_status_type.PENDING:
        raise ValueError("Only pending orders can be cancelled")

    order.status = order_status_type.CANCELLED

    for item in order.order_items:
        product = item.product
        product.stock += item.quantity

        movement = InventoryMovement(
            product_id=product.id,
            type=movements_type.IN,
            quantity=item.quantity,
            reason="order_cancelled",
            created_by=cancelled_by
        )
        db.add(movement)

    db.commit()
    db.refresh(order)
    return order

def _is_valid_status_change(current: OrderStatus, new: OrderStatus) -> bool:
    allowed_transitions = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
        OrderStatus.PREPARING: {OrderStatus.SENT},
        OrderStatus.SENT: {OrderStatus.DELIVERED},
        OrderStatus.DELIVERED: set(),
        OrderStatus.CANCELLED: set()
    }
    return new in allowed_transitions.get(current, set())
