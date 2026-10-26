import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"
st.set_page_config(page_title="Inventory & Sales", page_icon="📦", layout="wide")


def call_api(method, path, **kwargs):
    """Calls the FastAPI backend. Returns (data, error_message)."""
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    try:
        r = requests.request(method, f"{API}{path}", headers=headers, timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Start it first: `uvicorn main:app --reload` (inside the backend folder)")
        st.stop()
    if r.status_code == 401 and st.session_state.get("token"):
        # token expired or invalid -> force a fresh login
        st.session_state.clear()
        st.rerun()
    if r.status_code >= 400:
        detail = r.json().get("detail", "Something went wrong")
        if isinstance(detail, list):  # validation errors
            detail = detail[0].get("msg", "Invalid input")
        return None, detail
    return r.json(), None

def show(err, ok_message):
    if err:
        st.error(err)
    else:
        st.success(ok_message)


# ---------------- LOGIN / REGISTER ----------------
def save_login(data):
    """Keep the user logged in, then open the Dashboard."""
    st.session_state["token"] = data["token"]
    st.session_state["username"] = data["username"]
    st.session_state["page"] = "Dashboard"  # land on the main page
    st.rerun()


if "token" not in st.session_state:
    # after a successful registration, switch back to the Login view
    if st.session_state.pop("go_to_login", False):
        st.session_state["auth_mode"] = "Login"

    st.title("📦 Inventory & Sales")
    mode = st.radio("Choose", ["Login", "Register"], horizontal=True,
                    key="auth_mode", label_visibility="collapsed")

    if mode == "Login":
        if "flash" in st.session_state:
            st.success(st.session_state.pop("flash"))
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            go = st.form_submit_button("Login")
        if go:
            data, err = call_api("POST", "/login", json={"username": u, "password": p})
            if err:
                st.error(err)
            else:
                save_login(data)  # goes to the Dashboard

    else:  # Register
        with st.form("register_form"):
            u2 = st.text_input("Enter your Username")
            p2 = st.text_input("Enter your Password (min 6 characters)", type="password")
            p3 = st.text_input("Confirm password", type="password")
            go2 = st.form_submit_button("Create account")
        if go2:
            if p2 != p3:
                st.error("Passwords do not match")
            else:
                data, err = call_api("POST", "/register", json={"username": u2, "password": p2})
                if err:
                    st.error(err)
                else:
                    # do NOT log in yet: send the user to the Login page
                    st.session_state["flash"] = "Account created! Please log in."
                    st.session_state["go_to_login"] = True
                    st.rerun()

    st.stop()  # nothing below runs until the user is logged in


st.sidebar.title("📦 Inventory & Sales")
page = st.sidebar.radio("Go to", ["Dashboard", "Products", "Add Product", "Make a Sale", "Sales History"], key="page")

st.sidebar.divider()
st.sidebar.write(f"👤 Logged in as **{st.session_state['username']}**")
if st.sidebar.button("Logout"):
    call_api("POST", "/logout")
    st.session_state.clear()
    st.rerun()

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("Dashboard")
    data, err = call_api("GET", "/dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", data["total_products"])
    c2.metric("Units in stock", data["total_units_in_stock"])
    c3.metric("Total sales", data["total_sales"])
    c4.metric("Revenue", f"₹{data['total_revenue']:,.2f}")

    left, right = st.columns(2)
    with left:
        st.subheader("⚠️ Low stock")
        if data["low_stock"]:
            st.dataframe(pd.DataFrame(data["low_stock"]), use_container_width=True, hide_index=True)
        else:
            st.success("All products are well stocked.")
    with right:
        st.subheader("🏆 Top products by revenue")
        if data["top_products"]:
            st.bar_chart(pd.DataFrame(data["top_products"]).set_index("name"))
        else:
            st.info("No sales yet.")

# ---------------- PRODUCTS ----------------
elif page == "Products":
    st.title("Products")
    products, err = call_api("GET", "/products")
    if not products:
        st.info("No products yet. Add one from the sidebar.")
    else:
        st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)

        st.subheader("Edit or delete")
        choice = st.selectbox("Pick a product", products, format_func=lambda p: f"{p['id']} - {p['name']}")
        with st.form("edit_form"):
            name = st.text_input("Name", choice["name"])
            category = st.text_input("Category", choice["category"])
            price = st.number_input("Price", min_value=0.01, value=float(choice["price"]))
            stock = st.number_input("Stock", min_value=0, value=int(choice["stock"]))
            reorder = st.number_input("Reorder level", min_value=0, value=int(choice["reorder_level"]))
            save = st.form_submit_button("Save changes")
        if save:
            body = {"name": name, "category": category, "price": price, "stock": stock, "reorder_level": reorder}
            _, err = call_api("PUT", f"/products/{choice['id']}", json=body)
            # st.error(err) if err else st.success("Updated!")
            show(err, "Updated!")

        if st.button("🗑️ Delete this product"):
            _, err = call_api("DELETE", f"/products/{choice['id']}")
            # st.error(err) if err else st.success("Deleted! Refresh the page.")
            show(err, "Deleted! Refresh the page.")

# ---------------- ADD PRODUCT ----------------
elif page == "Add Product":
    st.title("Add a product")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        category = st.text_input("Category", "General")
        price = st.number_input("Price", min_value=0.01, value=100.0)
        stock = st.number_input("Opening stock", min_value=0, value=10)
        reorder = st.number_input("Reorder level (low-stock alert)", min_value=0, value=5)
        submit = st.form_submit_button("Add product")
    if submit:
        body = {"name": name, "category": category, "price": price, "stock": stock, "reorder_level": reorder}
        _, err = call_api("POST", "/products", json=body)
        # st.error(err) if err else st.success(f"'{name}' added!")
        show(err, f"'{name}' added!")

# ---------------- MAKE A SALE ----------------
elif page == "Make a Sale":
    st.title("Record a sale")
    products, err = call_api("GET", "/products")
    if not products:
        st.info("Add some products first.")
    else:
        product = st.selectbox(
            "Product", products,
            format_func=lambda p: f"{p['name']}  (₹{p['price']}, {p['stock']} in stock)",
        )
        qty = st.number_input("Quantity", min_value=1, value=1)
        st.write(f"**Total: ₹{product['price'] * qty:,.2f}**")
        if st.button("Confirm sale"):
            _, err = call_api("POST", "/sales", json={"product_id": product["id"], "quantity": qty})
            # st.error(err) if err else st.success("Sale recorded and stock updated!")
            show(err, "Sale recorded and stock updated!")

# ---------------- SALES HISTORY ----------------
elif page == "Sales History":
    st.title("Sales history")
    sales, err = call_api("GET", "/sales")
    if not sales:
        st.info("No sales yet.")
    else:
        df = pd.DataFrame(sales)
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False), "sales.csv", "text/csv")
