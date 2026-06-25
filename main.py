from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# ====================== HOME ======================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with engine.connect() as conn:
        total_sales = conn.execute(text("SELECT COALESCE(SUM(total_amount), 0) as total FROM sales")).scalar()
        total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        low_stock_count = conn.execute(text("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")).scalar()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sales Inventory System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f8f9fa; }}
            .navbar {{ background: #2c3e50 !important; }}
            .hero {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 60px 0; text-align: center; }}
            .stat-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/">🏪 Sales Inventory</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/products">Products</a>
                    <a class="nav-link" href="/low-stock">Low Stock</a>
                    <a class="nav-link" href="/best-sellers">Best Sellers</a>
                    <a class="nav-link" href="/add-product">Add Product</a>
                    <a class="nav-link" href="/record-sale">Record Sale</a>
                </div>
            </div>
        </nav>

        <div class="hero">
            <div class="container">
                <h1>Welcome to Sales Inventory System</h1>
                <p class="lead">Manage your business efficiently</p>
            </div>
        </div>

        <div class="container mt-5">
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="stat-card">
                        <h5>Total Sales</h5>
                        <h2>£{total_sales:,}</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <h5>Total Products</h5>
                        <h2>{total_products}</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <h5>Low Stock Items</h5>
                        <h2 style="color:red">{low_stock_count}</h2>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)
# ====================== PRODUCTS ======================
@app.get("/products", response_class=HTMLResponse)
async def products(request: Request, search: str = None):
    query = "SELECT p.product_id, p.product_name, c.category_name, p.price, p.stock_quantity FROM products p LEFT JOIN categories c ON p.category_id = c.category_id"
    if search:
        query += " WHERE p.product_name ILIKE :search"
    query += " ORDER BY p.product_id"
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"search": f"%{search}%" if search else None})
        products_list = [dict(row) for row in result.mappings()]
    
    html = """
    <div class="container mt-4">
        <h2>📦 All Products</h2>
        <form method="get" class="mb-3">
            <div class="input-group">
                <input type="text" class="form-control" name="search" placeholder="Search products..." value="{{ request.query_params.get('search', '') }}">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        <table class="table table-striped table-hover">
            <thead><tr><th>ID</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th></tr></thead>
            <tbody>
    """
    for p in products_list:
        html += f"<tr><td>{p['product_id']}</td><td>{p['product_name']}</td><td>{p.get('category_name','N/A')}</td><td>£{p['price']}</td><td>{p['stock_quantity']}</td></tr>"
    html += "</tbody></table></div>"
    return HTMLResponse(html)

# ====================== LOW STOCK ======================
@app.get("/low-stock", response_class=HTMLResponse)
async def low_stock(request: Request):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT p.product_name, c.category_name, p.stock_quantity FROM products p LEFT JOIN categories c ON p.category_id = c.category_id WHERE p.stock_quantity < 10 ORDER BY p.stock_quantity"))
        items = [dict(row) for row in result.mappings()]
    
    html = """
    <div class="container mt-4">
        <h2>⚠️ Low Stock Items</h2>
        <table class="table table-striped table-hover">
            <thead><tr><th>Product</th><th>Category</th><th>Stock</th></tr></thead>
            <tbody>
    """
    for item in items:
        html += f"<tr class='table-danger'><td>{item['product_name']}</td><td>{item.get('category_name','N/A')}</td><td><b>{item['stock_quantity']}</b></td></tr>"
    html += "</tbody></table></div>"
    return HTMLResponse(html)

# ====================== BEST SELLERS ======================
@app.get("/best-sellers", response_class=HTMLResponse)
async def best_sellers(request: Request):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT p.product_name, SUM(s.quantity) as total_sold FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.product_name ORDER BY total_sold DESC LIMIT 10"))
        best = [dict(row) for row in result.mappings()]
    
    html = """
    <div class="container mt-4">
        <h2>🔥 Best Sellers</h2>
        <table class="table table-striped table-hover">
            <thead><tr><th>Rank</th><th>Product</th><th>Total Sold</th></tr></thead>
            <tbody>
    """
    for i, item in enumerate(best, 1):
        html += f"<tr><td>{i}</td><td>{item['product_name']}</td><td>{item['total_sold']}</td></tr>"
    html += "</tbody></table></div>"
    return HTMLResponse(html)

# ====================== ADD PRODUCT ======================
@app.get("/add-product", response_class=HTMLResponse)
async def add_product_form(request: Request):
    html = """
    <div class="container mt-4">
        <h2>➕ Add New Product</h2>
        <form method="post" action="/add-product">
            <div class="mb-3">
                <label>Product Name</label>
                <input type="text" class="form-control" name="product_name" required>
            </div>
            <div class="mb-3">
                <label>Category ID</label>
                <input type="number" class="form-control" name="category_id" required>
            </div>
            <div class="mb-3">
                <label>Price</label>
                <input type="number" step="0.01" class="form-control" name="price" required>
            </div>
            <div class="mb-3">
                <label>Stock Quantity</label>
                <input type="number" class="form-control" name="stock_quantity" required>
            </div>
            <button type="submit" class="btn btn-success">Add Product</button>
        </form>
    </div>
    """
    return HTMLResponse(html)

@app.post("/add-product")
async def add_product(product_name: str = Form(...), category_id: int = Form(...), price: float = Form(...), stock_quantity: int = Form(...)):
    try:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO products (product_name, category_id, price, stock_quantity) VALUES (:name, :cat, :price, :stock)"), 
                        {"name": product_name, "cat": category_id, "price": price, "stock": stock_quantity})
            conn.commit()
        return RedirectResponse(url="/products", status_code=303)
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}<br><a href='/add-product'>Try Again</a>")

# ====================== RECORD SALE ======================
@app.get("/record-sale", response_class=HTMLResponse)
async def record_sale_form(request: Request):
    with engine.connect() as conn:
        products = conn.execute(text("SELECT product_id, product_name, price FROM products")).mappings().all()
    html = """
    <div class="container mt-4">
        <h2>💰 Record Sale</h2>
        <form method="post" action="/record-sale">
            <div class="mb-3">
                <label>Product</label>
                <select class="form-control" name="product_id">
    """
    for p in products:
        html += f"<option value='{p['product_id']}'>{p['product_name']} (£{p['price']})</option>"
    html += """
                </select>
            </div>
            <div class="mb-3">
                <label>Quantity</label>
                <input type="number" class="form-control" name="quantity" required>
            </div>
            <button type="submit" class="btn btn-success">Record Sale</button>
        </form>
    </div>
    """
    return HTMLResponse(html)

@app.post("/record-sale")
async def record_sale(product_id: int = Form(...), quantity: int = Form(...)):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT price, stock_quantity FROM products WHERE product_id = :pid"), {"pid": product_id})
            product = result.first()
            if not product or product.stock_quantity < quantity:
                return HTMLResponse("Not enough stock!<br><a href='/record-sale'>Go Back</a>")
            
            total_amount = product.price * quantity
            
            conn.execute(text("INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (:pid, :qty, :total, CURRENT_DATE)"), 
                        {"pid": product_id, "qty": quantity, "total": total_amount})
            conn.execute(text("UPDATE products SET stock_quantity = stock_quantity - :qty WHERE product_id = :pid"), 
                        {"qty": quantity, "pid": product_id})
            conn.commit()
        return RedirectResponse(url="/products", status_code=303)
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}<br><a href='/record-sale'>Try Again</a>")

print("✅ Full Professional Bootstrap App Running!")