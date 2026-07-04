from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from database import engine

router = APIRouter()

@router.get("/record-sale", response_class=HTMLResponse)
async def record_sale_form(request: Request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Record Sale</title>
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
                <div class="card-header bg-success text-white">
                    <h3>💰 Record New Sale</h3>
                </div>
                <div class="card-body">
                    <form method="post" action="/record-sale">
                        <div class="mb-3">
                            <label class="form-label">Product ID</label>
                            <input type="number" name="product_id" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Quantity Sold</label>
                            <input type="number" name="quantity" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-success">Record Sale</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

@router.post("/record-sale")
async def record_sale(product_id: int = Form(...), quantity: int = Form(...)):
    try:
        with engine.connect() as conn:
            # Record the sale
            conn.execute(text("""
                INSERT INTO sales (product_id, quantity, sale_date, total_amount)
                SELECT :pid, :qty, CURRENT_DATE, price * :qty 
                FROM products WHERE product_id = :pid
            """), {"pid": product_id, "qty": quantity})
            
            # Reduce stock
            conn.execute(text("""
                UPDATE products 
                SET stock_quantity = stock_quantity - :qty 
                WHERE product_id = :pid
            """), {"pid": product_id, "qty": quantity})
            
            conn.commit()
        return RedirectResponse(url="/products", status_code=303)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")