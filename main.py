from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},

    # Added products (Question 1)
    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1499, "category": "Electronics", "in_stock": False}
]


@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered_products = []

    for product in products:
        if product["category"].lower() == category_name.lower():
            filtered_products.append(product)

    if len(filtered_products) == 0:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products
    }


@app.get("/products/instock")
def get_instock_products():

    instock_products = []

    for product in products:
        if product["in_stock"] == True:
            instock_products.append(product)

    return {
        "in_stock_products": instock_products,
        "count": len(instock_products)
    }

@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    instock = 0
    outstock = 0
    categories = set()

    for product in products:

        categories.add(product["category"])

        if product["in_stock"]:
            instock += 1
        else:
            outstock += 1

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": list(categories)
    }

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            matched_products.append(product)

    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "total_matches": len(matched_products)
    }

@app.get("/products/deals")
def product_deals():

    cheapest_product = min(products, key=lambda x: x["price"])
    expensive_product = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest_product,
        "premium_pick": expensive_product
    }