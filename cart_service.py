import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

PRODUCT_SERVICE_URL = "https://saas-product-service.onrender.com"

carts = {}


@app.route('/', methods=['GET'])
def home():
    return "Welcome to your cart!", 200


@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    user_cart = carts.get(user_id, [])

    response = requests.get(f'{PRODUCT_SERVICE_URL}/products')
    if response.status_code != 200:
        return jsonify({"error": "Unable to retrieve products from the product service."}), 500

    all_products = response.json().get("products", [])
    cart_contents = []
    total_price = 0

    for item in user_cart:
        product = next((p for p in all_products if p["id"] == item["id"]), None)
        if product:
            quantity = item["quantity"]
            price_for_product = product["price"] * quantity
            total_price += price_for_product
            cart_contents.append({
                "product_name": product["product_name"],
                "quantity": quantity,
                "total_price": price_for_product
            })

    return jsonify({
        "cart_contents": cart_contents,
        "total_price": total_price
    })


@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)

    response = requests.get(f'{PRODUCT_SERVICE_URL}/products/{product_id}')
    if response.status_code != 200:
        return jsonify({"error": "Product not found."}), 404

    if user_id not in carts:
        carts[user_id] = []

    product_in_cart = next((item for item in carts[user_id] if item["id"] == product_id), None)
    if product_in_cart:
        product_in_cart["quantity"] += quantity
    else:
        carts[user_id].append({
            "id": product_id,
            "quantity": quantity
        })

    return jsonify({"message": f"Added {quantity} of product to cart", "cart": carts[user_id]}), 201


@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    quantity_to_remove = request.json.get('quantity', None)

    if user_id not in carts:
        return jsonify({"error": "No cart found for the user."}), 404

    product_in_cart = next((item for item in carts[user_id] if item["id"] == product_id), None)
    if not product_in_cart:
        return jsonify({"error": "Product not found in cart."}), 404

    if quantity_to_remove:
        product_in_cart["quantity"] -= quantity_to_remove

        if product_in_cart["quantity"] <= 0:
            carts[user_id] = [item for item in carts[user_id] if item["id"] != product_id]
    else:
        carts[user_id] = [item for item in carts[user_id] if item["id"] != product_id]

    return jsonify({"message": f"Removed {quantity_to_remove} of product from cart", "cart": carts[user_id]}), 200


if __name__ == '__main__':
    app.run(debug=True)
