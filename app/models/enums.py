from enum import Enum

class users_role(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CLIENT = "client"

class order_status_type(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    SENT = "sent"
    CANCELLED = "cancelled"

class movements_type(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"