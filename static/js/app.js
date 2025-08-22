window.GiftShop = (function () {
  async function getJSON(url, opts={}) {
    const res = await fetch(url, { headers: { "Content-Type": "application/json" }, credentials: "same-origin", ...opts });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function loadProducts() {
    const root = document.getElementById("products");
    const products = await getJSON("/api/products");
    root.innerHTML = products.map(p => `
      <div class="card">
        <img src="${p.image || 'https://via.placeholder.com/300x160?text=Gift'}" alt="${p.name}">
        <h3>${p.name}</h3>
        <p>$${p.price.toFixed(2)}</p>
        <button class="btn" onclick="GiftShop.addToCart(${p.id})">Add to Cart</button>
      </div>`).join("");
  }

  async function addToCart(productId) {
    await getJSON("/api/cart/add", { method: "POST", body: JSON.stringify({ product_id: productId, qty: 1 }) });
    alert("Added to cart!");
  }

  function renderCart(data) {
    const root = document.getElementById("cart");
    const totalEl = document.getElementById("cart-total");
    if (!root || !totalEl) return;
    if (data.items.length === 0) {
      root.innerHTML = "<p>Your cart is empty.</p>";
      totalEl.textContent = "";
      return;
    }
    root.innerHTML = data.items.map((row) => `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div><strong>${row.product.name}</strong><br>$${row.product.price.toFixed(2)} each</div>
          <div>
            <input type="number" min="0" value="${row.qty}" style="width:70px"
                   onchange="GiftShop.updateQty(${row.product.id}, this.value)">
            <div style="text-align:right;">Line: $${row.line_total.toFixed(2)}</div>
          </div>
        </div>
      </div>
    `).join("");
    totalEl.textContent = `Total: $${data.total.toFixed(2)}`;
  }

  async function loadCart() {
    const data = await getJSON("/api/cart");
    renderCart(data);
  }

  async function updateQty(productId, qty) {
    const data = await getJSON("/api/cart/update", { method: "POST", body: JSON.stringify({ product_id: productId, qty: Number(qty) }) });
    renderCart(data);
  }

  async function clearCart() {
    const data = await getJSON("/api/cart/clear", { method: "POST" });
    renderCart(data);
  }

  function bindCheckout() {
    const form = document.getElementById("checkout-form");
    const msg = document.getElementById("checkout-message");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      try {
        const data = await getJSON("/api/checkout", {
          method: "POST",
          body: JSON.stringify({ name: formData.get("name"), address: formData.get("address") })
        });
        msg.textContent = data.message;
        form.reset();
      } catch (err) {
        msg.textContent = "Checkout failed: " + err.message;
      }
    });
  }

  return { loadProducts, addToCart, loadCart, updateQty, clearCart, bindCheckout };
})();
