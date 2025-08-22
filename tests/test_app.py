import json
from app import app

def test_products_list():
    client = app.test_client()
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list) and len(data) >= 1

def test_cart_add_and_get():
    client = app.test_client()
    res = client.post("/api/cart/add", json={"product_id": 1, "qty": 2})
    assert res.status_code == 200
    res = client.get("/api/cart")
    data = res.get_json()
    assert data["items"][0]["qty"] == 2
    assert data["total"] > 0

def test_checkout_empty_cart():
    client = app.test_client()
    client.post("/api/cart/clear")
    res = client.post("/api/checkout", json={"name": "Test", "address": "Nowhere"})
    assert res.status_code == 400
