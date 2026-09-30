from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from core.config import settings
from .auth import router as auth_router
from .categories import router as category_router
from .products import router as product_router
from .attributes import router as attributes_router
from .product_variants import router as product_variants_router
from .cart import router as cart_router
from .order import router as order_router

tags_metadata = [
    {
        "name": "user",
        "description": "User endpoints",
    },
    {
        "name": "categories",
        "description": "Public category endpoints",
    },
    {
        "name": "attributes",
        "description": "Public Attributes endpoints",
    },
    {
        "name": "products",
        "description": "Public product endpoints",
    },
    {
        "name": "variants",
        "description": "Public variant endpoints",
    },
    {
        "name": "cart",
        "description": "cart endpoints",
    },
    {
        "name": "order",
        "description": "order endpoints",
    },
    {
        "name": "admin",
        "description": "Admin public operations",
    }
    ,
    {
        "name": "admin-categories",
        "description": "Admin operations for categories",
    },
    {
        "name": "admin-attributes",
        "description": "Admin operations for attributes"
    },
    {
        "name": "admin-products",
        "description": "Admin operations for products",
    },
    {
        "name": "admin-variants",
        "description": "Admin operations for product variants",
    },
    {
        "name": "admin-cart",
        "description": "Admin operations for cart",
    },
]
app = FastAPI(openapi_tags=tags_metadata)
app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(product_router.router)
app.include_router(attributes_router.router)
app.include_router(product_variants_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)

if settings.ENVIRONMENT == "development":
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"message": "Hello World"}
