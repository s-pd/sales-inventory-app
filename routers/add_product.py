from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from database import engine

router = APIRouter()

@router.get("/add-product", response_class=HTMLResponse)
async def add_product_form(request: Request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Product</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Sales Inventory</a>
                <a class="btn btn-outline-light" href="/">← Back to Home</a>
            </div>
        </nav>
        
        <div class="container mt-5">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h3>➕ Add New Product</h3>
                </div>
                <div class="card-body">
                    <form method="post" action="/add-product">
                        <div class="mb-3">
                            <label class="form-label">Product Name</label>
                            <input type="text" name="product_name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Category ID</label>
                            <input type="number" name="category_id" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Price (£)</label>
                            <input type="number" step="0.01" name="price" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Stock Quantity</label>
                            <input type="number" name="stock_quantity" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-success">Add Product</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

@router.post("/add-product")
async def add_product(product_name: str = Form(...), category_id: int = Form(...), 
                     price: float = Form(...), stock_quantity: int = Form(...)):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO products (product_name, category_id, price, stock_quantity)
                VALUES (:name, :cat, :price, :stock)
            """), {"name": product_name, "cat": category_id, "price": price, "stock": stock_quantity})
            conn.commit()
        return RedirectResponse(url="/products", status_code=303)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")