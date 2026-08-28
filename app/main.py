from fastapi import FastAPI

from .auth import router as auth_router
from .categories import router as category_router
from .products import router as product_router
from .attributes import router as attributes_router
from .product_variants import router as product_variants_router

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
]
app = FastAPI(openapi_tags=tags_metadata)
app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(product_router.router)
app.include_router(attributes_router.router)

app.include_router(product_variants_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
