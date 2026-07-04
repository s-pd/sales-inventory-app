from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from database import engine

router = APIRouter()

@router.get("/low-stock", response_class=HTMLResponse)
async def low_stock(request: Request):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.product_name, c.category_name, p.stock_quantity 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.stock_quantity < 10 
                ORDER BY p.stock_quantity ASC
            """))
            items = [dict(row) for row in result.mappings()]

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Low Stock - Sales Inventory</title>
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
                <h2 class="text-danger">⚠️ Low Stock Items</h2>
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Stock Remaining</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr class='table-danger'><td>{item['product_name']}</td><td>{item.get('category_name','N/A')}</td><td><b>{item['stock_quantity']}</b></td></tr>" for item in items)}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")