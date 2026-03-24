from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()


#  Product data
products = [
    {"id": 1, "name": "Laptop", "price": 50000, "category": "electronics", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 499, "category": "electronics", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "electronics", "in_stock": False},
    {"id": 4, "name": "Notebook", "price": 50, "category": "stationery", "in_stock": True},
]

#  Feedback storage (OUTSIDE model)
feedback = []

@app.get("/products")
def get_all_products():
    return products

#  Pydantic model
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

#  Each item in order
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

#  Bulk order request
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)    


#  Filter endpoint
@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):
    filtered_products = products

    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]

    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]

    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    return filtered_products


#  Price endpoint
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}


#  Feedback endpoint
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())  # use data.model_dump() if Pydantic v2
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback),
    }

@app.get("/products/summary")
def product_summary():
    total_products = len(products)

    in_stock_count = sum(1 for p in products if p["in_stock"])
    out_of_stock_count = total_products - in_stock_count

    # Most expensive product
    most_expensive_product = max(products, key=lambda x: x["price"])

    # Cheapest product
    cheapest_product = min(products, key=lambda x: x["price"])

    # Unique categories
    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        },
        "cheapest": {
            "name": cheapest_product["name"],
            "price": cheapest_product["price"]
        },
        "categories": categories
    }

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        # Find product
        product = next((p for p in products if p["id"] == item.product_id), None)

        #  Product not found
        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        #  Out of stock
        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        #  Valid item
        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }