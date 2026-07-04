from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from database import engine   # Direct import (not relative)

router = APIRouter()

@router.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    search = request.query_params.get("search", "")
    
    try:
        with engine.connect() as conn:
            if search:
                result = conn.execute(text("""
                    SELECT p.product_name, c.category_name, p.price, p.stock_quantity 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE p.product_name ILIKE :search 
                    ORDER BY p.product_name
                """), {"search": f"%{search}%"})
            else:
                result = conn.execute(text("""
                    SELECT p.product_name, c.category_name, p.price, p.stock_quantity 
                    FROM products p 
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    ORDER BY p.product_name
                """))
            
            products_list = [dict(row) for row in result.mappings()]

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Products - Sales Inventory</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Sales Inventory</a>
                    <a class="btn btn-outline-light" href="/">← Back to Home</a>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h2>📦 All Products</h2>
                
                <form method="get" class="mb-4">
                    <div class="input-group">
                        <input type="text" name="search" class="form-control" placeholder="Search products..." value="{search}">
                        <button class="btn btn-primary" type="submit">Search</button>
                        {f'<a href="/products" class="btn btn-secondary">Clear</a>' if search else ''}
                    </div>
                </form>

                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Price (£)</th>
                            <th>Stock</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr><td>{p['product_name']}</td><td>{p.get('category_name','N/A')}</td><td>£{p['price']}</td><td>{p['stock_quantity']}</td></tr>" for p in products_list)}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")