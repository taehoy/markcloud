from fastapi import FastAPI, Query

from routers.product_router import ProductRouter

app = FastAPI()

app.include_router(ProductRouter)
