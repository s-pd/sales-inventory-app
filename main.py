from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="Sales Inventory System")

style = """
<style>
    body {font-family: Arial, sans-serif; margin:0; background:#f8f9fa;}
    h1 {color:#2c3e50;}
    .container {max-width:1100px; margin:20px auto; padding:20px; background:white; border-radius:10px; box-shadow:0 4px 15px rgba(0,0,0,0.1);}
    nav {background:#2c3e50; padding:15px; text-align:center;}
    nav a {color:white; margin:0 15px; text-decoration:none; font-weight:bold;}
    table {width:100%; border-collapse:collapse; margin:15px 0;}
    th, td {padding:12px; text-align:left; border-bottom:1px solid #ddd;}
    th {background:#34495e; color:white;}
    .btn {padding:10px 20px; background:#3498db; color:white; text-decoration:none; border-radius:5px; margin:5px; display:inline-block;}
</style>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><title>Sales Inventory</title>{style}</head><body>
        <nav>
            <a href="/">🏠 Home</a>
            <a href="/products">📦 Products</a>
            <a href="/low-stock">⚠️ Low Stock</a>
            <a href="/best-sellers">🔥 Best Sellers</a>
            <a href="/add-product">➕ Add Product</a>
            <a href="/record-sale">💰 Record Sale</a>
        </nav>
        <div class="container">
            <h1>Welcome to Sales Inventory System</h1>
            <p>Your app is live! 🎉</p>
        </div>
    </body></html>
    """

@app.get("/products", response_class=HTMLResponse)
def get_products():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT product_name, category_name, price, stock_quantity FROM products p LEFT JOIN categories c ON p.category_id = c.category_id ORDER BY p.product_name"))
            rows = [dict(row) for row in result.mappings()]
        html = f"<h1>📦 All Products</h1><table><tr><th>Product</th><th>Category</th><th>Price</th><th>Stock</th></tr>"
        for r in rows:
            html += f"<tr><td>{r['product_name']}</td><td>{r.get('category_name') or 'N/A'}</td><td>${r['price']}</td><td>{r['stock_quantity']}</td></tr>"
        html += "</table><br><a href='/' class='btn'>← Back</a>"
        return html
    except Exception as e:
        return f"<h2 style='color:red;'>Error: {str(e)}</h2><a href='/'>Back</a>"

@app.get("/low-stock", response_class=HTMLResponse)
def get_low_stock():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT product_name, category_name, stock_quantity FROM products p LEFT JOIN categories c ON p.category_id = c.category_id WHERE stock_quantity < 30 ORDER BY p.stock_quantity"))
            rows = [dict(row) for row in result.mappings()]
        html = f"<h1>⚠️ Low Stock Items</h1><table><tr><th>Product</th><th>Category</th><th>Stock</th></tr>"
        for r in rows:
            html += f"<tr><td>{r['product_name']}</td><td>{r.get('category_name') or 'N/A'}</td><td style='color:red;'><b>{r['stock_quantity']}</b></td></tr>"
        html += "</table><br><a href='/' class='btn'>← Back</a>"
        return html
    except Exception as e:
        return f"<h2 style='color:red;'>Error: {str(e)}</h2><a href='/'>Back</a>"

@app.get("/best-sellers", response_class=HTMLResponse)
def best_sellers():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT p.product_name, SUM(s.quantity) as total_sold, c.category_name FROM sales s JOIN products p ON s.product_id = p.product_id LEFT JOIN categories c ON p.category_id = c.category_id GROUP BY p.product_name, c.category_name ORDER BY total_sold DESC LIMIT 5"))
            rows = [dict(row) for row in result.mappings()]
        html = f"<h1>🔥 Top 5 Best Sellers</h1><table><tr><th>Rank</th><th>Product</th><th>Category</th><th>Total Sold</th></tr>"
        for i, r in enumerate(rows, 1):
            html += f"<tr><td>{i}</td><td>{r['product_name']}</td><td>{r.get('category_name') or 'N/A'}</td><td><b>{r['total_sold']}</b></td></tr>"
        html += "</table><br><a href='/' class='btn'>← Back</a>"
        return html
    except Exception as e:
        return f"<h2 style='color:red;'>Error: {str(e)}</h2><a href='/'>Back</a>"

@app.get("/add-product", response_class=HTMLResponse)
def add_product_form():
    return f"""
    <html><head><title>Add Product</title>{style}</head><body>
        <nav>...</nav>
        <div class="container">
            <h1>➕ Add New Product</h1>
            <form action="/add-product" method="post">
                <input type="text" name="product_name" placeholder="Product Name" required><br>
                <input type="number" name="price" placeholder="Price" step="0.01" required><br>
                <input type="number" name="stock_quantity" placeholder="Stock Quantity" required><br>
                <input type="number" name="category_id" placeholder="Category ID" required><br><br>
                <button type="submit" class="btn">Add Product</button>
            </form>
            <a href="/" class="btn">← Back</a>
        </div>
    </body></html>
    """

@app.post("/add-product")
def add_product(product_name: str = Form(...), price: float = Form(...), stock_quantity: int = Form(...), category_id: int = Form(...)):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO products (product_name, price, stock_quantity, category_id) VALUES (:name, :price, :stock, :cat)"), {"name": product_name, "price": price, "stock": stock_quantity, "cat": category_id})
        conn.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/record-sale", response_class=HTMLResponse)
def record_sale_form():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT product_id, product_name, stock_quantity FROM products ORDER BY product_name"))
        products = [dict(row) for row in result.mappings()]
    options = "".join([f"<option value='{p['product_id']}'>{p['product_name']} (Stock: {p['stock_quantity']})</option>" for p in products])
    
    return f"""
    <html><head><title>Record Sale</title>{style}</head><body>
        <nav>...</nav>
        <div class="container">
            <h1>💰 Record Sale</h1>
            <form action="/record-sale" method="post">
                <select name="product_id" required><option value="">-- Select Product --</option>{options}</select><br>
                <input type="number" name="quantity" placeholder="Quantity Sold" min="1" required><br><br>
                <button type="submit" class="btn">Record Sale</button>
            </form>
            <a href="/" class="btn">← Back</a>
        </div>
    </body></html>
    """

@app.post("/record-sale")
def record_sale(product_id: int = Form(...), quantity: int = Form(...)):
    try:
        with engine.connect() as conn:
            price_row = conn.execute(text("SELECT price FROM products WHERE product_id = :pid"), {"pid": product_id}).fetchone()
            if not price_row:
                return HTMLResponse("Product not found")
            total_amount = price_row[0] * quantity

            conn.execute(text("UPDATE products SET stock_quantity = stock_quantity - :qty WHERE product_id = :pid"), {"pid": product_id, "qty": quantity})
            conn.execute(text("INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (:pid, :qty, :total, CURRENT_DATE)"), {"pid": product_id, "qty": quantity, "total": total_amount})
            conn.commit()
        return RedirectResponse("/products", status_code=303)
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}")

print("✅ Full app with all routes is running!")