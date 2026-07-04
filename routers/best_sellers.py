from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from database import engine

router = APIRouter()

@router.get("/best-sellers", response_class=HTMLResponse)
async def best_sellers(request: Request):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.product_name, SUM(s.quantity) as total_sold
                FROM sales s 
                JOIN products p ON s.product_id = p.product_id
                GROUP BY p.product_name 
                ORDER BY total_sold DESC 
                LIMIT 10
            """))
            best = [dict(row) for row in result.mappings()]

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Best Sellers - Sales Inventory</title>
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
                <h2 class="text-warning">🔥 Top 10 Best Sellers</h2>
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Rank</th>
                            <th>Product Name</th>
                            <th>Total Sold</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr><td>{i+1}</td><td>{item['product_name']}</td><td><b>{item['total_sold']}</b></td></tr>" for i, item in enumerate(best))}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")