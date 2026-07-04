from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from database import engine   # Direct import

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        with engine.connect() as conn:
            total_sales = conn.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM sales")).scalar() or 0
            total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
            low_stock = conn.execute(text("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")).scalar() or 0

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sales Inventory</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; font-family: 'Segoe UI', sans-serif; }}
                .navbar {{ background: rgba(0,0,0,0.9) !important; }}
                .hero {{ background: rgba(255,255,255,0.95); border-radius: 20px; padding: 50px 30px; margin: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
                .stat-card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark">
                <div class="container">
                    <a class="navbar-brand fw-bold fs-4" href="/">Sales Inventory</a>
                    <div class="navbar-nav ms-auto">
                        <a class="nav-link mx-2" href="/products">Products</a>
                        <a class="nav-link mx-2" href="/low-stock">Low Stock</a>
                        <a class="nav-link mx-2" href="/best-sellers">Best Sellers</a>
                        <a class="nav-link mx-2" href="/add-product">Add Product</a>
                        <a class="nav-link mx-2" href="/record-sale">Record Sale</a>
                    </div>
                </div>
            </nav>

            <div class="hero text-center">
                <h1 class="display-4 fw-bold text-primary">Welcome to Sales Inventory System</h1>
                <p class="lead text-muted">Manage your business efficiently</p>
            </div>

            <div class="container">
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <h5>Total Sales</h5>
                            <h2 class="text-success">£{total_sales:,.2f}</h2>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <h5>Total Products</h5>
                            <h2 class="text-primary">{total_products}</h2>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <h5>Low Stock Items</h5>
                            <h2 class="text-danger">{low_stock}</h2>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<h1>Database Error: {str(e)}</h1>")