import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import timedelta

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.permanent_session_lifetime = timedelta(days=7)

# Fake product catalog (normally from DB)
PRODUCTS = [
    {"id": 1, "name": "Plush Teddy", "price": 19.99, "image": "/static/img/teddy.png"},
    {"id": 2, "name": "Scented Candle", "price": 12.49, "image": "/static/img/candle.png"},
    {"id": 3, "name": "Gift Mug", "price": 9.99, "image": "/static/img/mug.png"},
    {"id": 4, "name": "Chocolate Box", "price": 14.5, "image": "/static/img/choco.png"},
]

def _get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]

def _cart_items_and_total(cart):
    items = []
    total = 0.0
    for pid, qty in cart.items():
        prod = next((p for p in PRODUCTS if p["id"] == int(pid)), None)
        if not prod:
            continue
        line_total = prod["price"] * qty
        total += line_total
        items.append({
            "product": prod,
            "qty": qty,
            "line_total": round(line_total, 2)
        })
    return items, round(total, 2)

# ---------- Pages ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

@app.route("/checkout")
def checkout_page():
    return render_template("checkout.html")

# ---------- APIs ----------
@app.route("/api/products")
def api_products():
    return jsonify(PRODUCTS)

@app.route("/api/cart", methods=["GET"])
def api_cart_get():
    cart = _get_cart()
    items, total = _cart_items_and_total(cart)
    return jsonify({"items": items, "total": total})

@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json(force=True)
    pid = str(data.get("product_id"))
    qty = int(data.get("qty", 1))
    if not any(p["id"] == int(pid) for p in PRODUCTS):
        return jsonify({"error": "Invalid product"}), 400
    cart = _get_cart()
    cart[pid] = cart.get(pid, 0) + max(1, qty)
    session["cart"] = cart
    items, total = _cart_items_and_total(cart)
    return jsonify({"ok": True, "items": items, "total": total})

@app.route("/api/cart/update", methods=["POST"])
def api_cart_update():
    data = request.get_json(force=True)
    pid = str(data.get("product_id"))
    qty = max(0, int(data.get("qty", 0)))
    cart = _get_cart()
    if qty == 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    session["cart"] = cart
    items, total = _cart_items_and_total(cart)
    return jsonify({"ok": True, "items": items, "total": total})

@app.route("/api/cart/clear", methods=["POST"])
def api_cart_clear():
    session["cart"] = {}
    return jsonify({"ok": True, "items": [], "total": 0.0})

@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    # Simulate processing; in reality you’d charge via a payment gateway
    name = request.json.get("name")
    address = request.json.get("address")
    cart = _get_cart()
    items, total = _cart_items_and_total(cart)
    if not items:
        return jsonify({"error": "Cart is empty"}), 400
    # Clear cart after “purchase”
    session["cart"] = {}
    return jsonify({"ok": True, "message": f"Thanks {name}! Your order total is ${total:.2f}."})

# ---------- Run ----------
if __name__ == "__main__":
    # Public host + port 5000
    app.run(host="0.0.0.0", port=5000, debug=False)
