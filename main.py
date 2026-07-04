from fastapi import FastAPI
import os
from dotenv import load_dotenv

# Import all routers
from routers.home import router as home_router
from routers.products import router as products_router
from routers.low_stock import router as low_stock_router
from routers.best_sellers import router as best_sellers_router
from routers.add_product import router as add_product_router
from routers.record_sale import router as record_sale_router

load_dotenv()

app = FastAPI(title="Sales Inventory System")

# Include all routers
app.include_router(home_router)
app.include_router(products_router)
app.include_router(low_stock_router)
app.include_router(best_sellers_router)
app.include_router(add_product_router)
app.include_router(record_sale_router)

print("✅ Full Professional Sales Inventory App Running!")