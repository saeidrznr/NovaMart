from fastapi import FastAPI

from .auth import router as auth_router
from .categories import router as category_router
from .products import router as product_router
from .attributes import router as attributes_router

app = FastAPI()
app.include_router(auth_router.router)
app.include_router(category_router.router)
app.include_router(product_router.router)
app.include_router(attributes_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
