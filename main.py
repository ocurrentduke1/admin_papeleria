from app.core.config import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import user, supplier, product, orders, order_items, inventory_movement

from app.routes import auth, users, suppliers, products

settings = get_settings()

app = FastAPI(
    tittle=settings.APP_NAME,
    debug=settings.DEBUG,
    description="API para gestionar una papelería",
    version="1.0.0"
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(suppliers.router)
app.include_router(products.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}