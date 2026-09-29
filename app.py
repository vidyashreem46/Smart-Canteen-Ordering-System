import streamlit as st
import sqlite3
import pandas as pd
import qrcode
import socket
from datetime import datetime
from PIL import Image

# ==========================================
# 1. DATABASE CONFIGURATION & INITIALIZATION
# ==========================================
DB_FILE = 'canteen.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Create Tables safely if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            available INTEGER DEFAULT 1
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            order_status TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    ''')
    
    # 2. Smart Menu Population (Guarantees ALL items are present)
    existing_items = c.execute("SELECT category, name FROM menu").fetchall()
    existing_set = set((row['category'], row['name']) for row in existing_items)
    
    rich_menu = [
        # Breakfast
        ("Breakfast", "Idli", 30), ("Breakfast", "Vada", 25), ("Breakfast", "Masala Dosa", 60), 
        ("Breakfast", "Plain Dosa", 40), ("Breakfast", "Set Dosa", 50), ("Breakfast", "Poori", 50), 
        ("Breakfast", "Upma", 35), ("Breakfast", "Pongal", 45),
        # Main Course
        ("Main Course", "Veg Meals", 90), ("Main Course", "North Indian Meals", 120), 
        ("Main Course", "South Indian Meals", 100), ("Main Course", "Chapati Oota", 80), 
        ("Main Course", "Mudde Oota", 85), ("Main Course", "Veg Pulao", 70), 
        ("Main Course", "Bisibele Bath", 65), ("Main Course", "Curd Rice", 50), 
        ("Main Course", "Fried Rice", 80), ("Main Course", "Veg Noodles", 80),
        # Snacks
        ("Snacks", "Samosa", 20), ("Snacks", "Vada Pav", 25), ("Snacks", "French Fries", 60), 
        ("Snacks", "Veg Sandwich", 50), ("Snacks", "Gobi Manchurian", 80), 
        ("Snacks", "Paneer Manchurian", 100), ("Snacks", "Spring Roll", 70),
        # Chats
        ("Chats", "Pani Puri", 40), ("Chats", "Masala Puri", 45), ("Chats", "Bhel Puri", 45), 
        ("Chats", "Sev Puri", 45), ("Chats", "Dahi Puri", 50), ("Chats", "Pav Bhaji", 70), 
        ("Chats", "Samosa Chat", 50),
        # Hot Beverages
        ("Hot Beverages", "Tea", 15), ("Hot Beverages", "Coffee", 20), ("Hot Beverages", "Ginger Tea", 20), 
        ("Hot Beverages", "Lemon Tea", 20), ("Hot Beverages", "Hot Chocolate", 60),
        # Cold Beverages
        ("Cold Beverages", "Cold Coffee", 70), ("Cold Beverages", "Lassi", 40), 
        ("Cold Beverages", "Buttermilk", 20), ("Cold Beverages", "Milkshake", 80), 
        ("Cold Beverages", "Soft Drink", 30),
        # Fresh Juices
        ("Fresh Juices", "Fresh Lime", 30), ("Fresh Juices", "Orange Juice", 60), 
        ("Fresh Juices", "Mosambi Juice", 60), ("Fresh Juices", "Watermelon Juice", 50), 
        ("Fresh Juices", "Pineapple Juice", 60), ("Fresh Juices", "Mango Juice", 70), 
        ("Fresh Juices", "Pomegranate Juice", 80), ("Fresh Juices", "Mixed Fruit Juice", 75),
        # Desserts
        ("Desserts", "Gulab Jamun", 40), ("Desserts", "Ice Cream", 50), 
        ("Desserts", "Brownie", 80), ("Desserts", "Gajar Halwa", 60)
    ]
    
    # Insert only the items that don't already exist in the database
    for cat, name, price in rich_menu:
        if (cat, name) not in existing_set:
            c.execute("INSERT INTO menu (category, name, price, available) VALUES (?, ?, ?, 1)", (cat, name, price))
            
    conn.commit()
    conn.close()

# ==========================================
# 2. UTILITY FUNCTIONS
# ==========================================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_bill_text(order_id):
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    conn.close()
    
    if not order:
        return "Order not found."
    
    bill = f"""--------------------------------
       SMART RESTAURANT
          DIGITAL BILL
--------------------------------
Order ID : #{order['order_id']}
Table    : {order['table_number']}
Customer : {order['customer_name']}
Date     : {order['timestamp']}
--------------------------------
"""
    for item in items:
        bill += f"{item['item_name']} x {item['quantity']} \t ₹{item['subtotal']}\n"
    
    bill += f"""--------------------------------
TOTAL               ₹{order['total_amount']}

Payment: {order['payment_method']}
Status : {order['payment_status']}
--------------------------------
       Thank You!
--------------------------------"""
    return bill

# ==========================================
# 3. PAGE VIEW FUNCTIONS
# ==========================================

def page_qr_generator():
    st.title("📱 COMMON RESTAURANT QR")
    st.info("Ensure the laptop and customer's phone are on the same Wi-Fi network.")
    
    ip_address = get_local_ip()
    port = 8501
    url = f"http://{ip_address}:{port}/?mode=customer"
    
    st.write("### Scan this QR to open the digital menu")
    
    # Fixed QR Generation for robust Streamlit rendering
    qr = qrcode.make(url)
    qr_img = qr.get_image() # Extracts the pure PIL Image
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(qr_img, width=400, caption="Point phone camera here")
    
    st.code(url, language="text")
    st.warning("Only ONE QR code is required for the entire restaurant. Customer selects their table in the app.")

def page_customer_flow():
    st.title("🍴 DIGITAL MENU & ORDERING")
    
    if 'customer_step' not in st.session_state:
        st.session_state.customer_step = 1
    if 'current_order_id' not in st.session_state:
        st.session_state.current_order_id = None
        
    # --- STEP 1: Registration ---
    if st.session_state.customer_step == 1:
        st.header("Welcome!")
        st.write("Please select your table and enter your name to continue.")
        table = st.selectbox("Select Your Table", ["Table 1", "Table 2", "Table 3", "Table 4"])
        name = st.text_input("Customer Name")
        
        if st.button("Browse Menu", type="primary"):
            if name.strip() == "":
                st.error("Please enter your name.")
            else:
                st.session_state.table = table.split(" ")[1]
                st.session_state.name = name
                st.session_state.customer_step = 2
                st.rerun()
                
    # --- STEP 2: Menu & Ordering ---
    elif st.session_state.customer_step == 2:
        st.subheader(f"Table {st.session_state.table} - Customer: {st.session_state.name}")
        
        conn = get_db_connection()
        # Fetch ordered by category to keep it structured
        df_menu = pd.read_sql("SELECT category, name, price FROM menu WHERE available=1 ORDER BY category, name", conn)
        conn.close()
        
        if df_menu.empty:
            st.warning("Menu is currently empty.")
            return

        st.write("### Search & Order")
        search = st.text_input("Search menu...")
        if search:
            df_menu = df_menu[df_menu['name'].str.contains(search, case=False) | df_menu['category'].str.contains(search, case=False)]
        
        # Add a quantity column
        df_menu.insert(0, "Order Qty", 0)
        
        st.info("Type the quantity you want next to the items below:")
        edited_df = st.data_editor(
            df_menu,
            column_config={
                "Order Qty": st.column_config.NumberColumn("Order Qty", min_value=0, max_value=50, step=1),
                "category": st.column_config.TextColumn("Category"),
                "name": st.column_config.TextColumn("Dish Name"),
                "price": st.column_config.NumberColumn("Price (₹)", format="₹%d")
            },
            disabled=["category", "name", "price"],
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        # Calculate Cart
        cart = edited_df[edited_df["Order Qty"] > 0]
        
        st.markdown("---")
        st.write("### 🛒 CART SUMMARY")
        
        if cart.empty:
            st.write("Your cart is empty.")
        else:
            total = 0
            for index, row in cart.iterrows():
                subtotal = row['Order Qty'] * row['price']
                total += subtotal
                st.write(f"{row['name']} x {row['Order Qty']} = **₹{subtotal}**")
            
            st.write(f"### Grand Total: ₹{total}")
            
            pay_method = st.radio("Select Payment Method:", ["Online Payment", "Cash to Waiter"])
            
            if st.button("PLACE ORDER", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                
                c.execute('''INSERT INTO orders 
                            (table_number, customer_name, total_amount, order_status, payment_method, payment_status) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (st.session_state.table, st.session_state.name, total, "New", pay_method, "Pending"))
                
                order_id = c.lastrowid
                
                for index, row in cart.iterrows():
                    subtotal = row['Order Qty'] * row['price']
                    c.execute('''INSERT INTO order_items (order_id, item_name, quantity, price, subtotal)
                                 VALUES (?, ?, ?, ?, ?)''',
                             (order_id, row['name'], row['Order Qty'], row['price'], subtotal))
                
                conn.commit()
                conn.close()
                
                st.session_state.current_order_id = order_id
                st.session_state.customer_step = 3
                st.success("Order Placed Successfully!")
                st.rerun()

    # --- STEP 3: Tracking & Payment ---
    elif st.session_state.customer_step == 3:
        st.subheader("Order Tracking")
        
        order_id = st.session_state.current_order_id
        conn = get_db_connection()
        order = conn.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
        conn.close()
        
        st.write(f"**Order ID:** #{order['order_id']} | **Table:** {order['table_number']}")
        
        status = order['order_status']
        if status == "New":
            st.info("🕒 Sent to Kitchen (NEW)")
        elif status == "Preparing":
            st.warning("👨‍🍳 Kitchen is PREPARING your food")
        elif status == "Ready":
            st.success("🔔 YOUR FOOD IS READY!")
        elif status == "Delivered":
            st.success("🍽️ FOOD DELIVERED. Enjoy your meal!")
            
        st.write(f"**Total Amount:** ₹{order['total_amount']}")
        
        st.markdown("---")
        st.write("### Payment & Bill")
        
        if order['payment_status'] == "Paid":
            st.success("✅ Payment Completed")
            bill_txt = generate_bill_text(order_id)
            st.text(bill_txt)
            st.download_button("Download Bill", data=bill_txt, file_name=f"bill_{order_id}.txt")
        else:
            st.warning(f"Payment Status: {order['payment_status']} via {order['payment_method']}")
            
            if order['payment_method'] == "Online Payment":
                if st.button("CONFIRM ONLINE PAYMENT (Demo)", type="primary"):
                    conn = get_db_connection()
                    conn.execute("UPDATE orders SET payment_status='Paid' WHERE order_id=?", (order_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
            else:
                st.info("Please hand over the cash to the waiter.")
                
        if st.button("Refresh Status"):
            st.rerun()
            
        if st.button("Place Another Order"):
            st.session_state.customer_step = 1
            st.rerun()


def page_kitchen():
    st.title("👨‍🍳 KITCHEN DASHBOARD")
    st.button("Refresh Orders")
    
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders WHERE order_status IN ('New', 'Preparing') ORDER BY timestamp ASC").fetchall()
    
    if not orders:
        st.success("No pending orders!")
    else:
        for order in orders:
            with st.container():
                st.markdown(f"### Order #{order['order_id']} - Table {order['table_number']}")
                st.write(f"**Customer:** {order['customer_name']} | **Status:** {order['order_status']}")
                
                items = conn.execute("SELECT item_name, quantity FROM order_items WHERE order_id=?", (order['order_id'],)).fetchall()
                for item in items:
                    st.write(f"- {item['item_name']} x {item['quantity']}")
                
                if order['order_status'] == 'New':
                    if st.button(f"START PREPARING ##{order['order_id']}"):
                        conn.execute("UPDATE orders SET order_status='Preparing' WHERE order_id=?", (order['order_id'],))
                        conn.commit()
                        st.rerun()
                elif order['order_status'] == 'Preparing':
                    if st.button(f"MARK FOOD READY ##{order['order_id']}", type="primary"):
                        conn.execute("UPDATE orders SET order_status='Ready' WHERE order_id=?", (order['order_id'],))
                        conn.commit()
                        st.rerun()
            st.markdown("---")
    conn.close()


def page_waiter():
    st.title("🧑‍🍳 WAITER DASHBOARD")
    st.button("Refresh Dashboard")
    
    conn = get_db_connection()
    
    st.header("🔔 Food Ready for Delivery")
    ready_orders = conn.execute("SELECT * FROM orders WHERE order_status = 'Ready'").fetchall()
    
    if not ready_orders:
        st.info("No food ready to be delivered.")
    else:
        for order in ready_orders:
            st.warning(f"**Order #{order['order_id']}** - Deliver to **Table {order['table_number']}** (Customer: {order['customer_name']})")
            if st.button(f"DELIVER TO TABLE ##{order['order_id']}", type="primary"):
                conn.execute("UPDATE orders SET order_status='Delivered' WHERE order_id=?", (order['order_id'],))
                conn.commit()
                st.rerun()
                
    st.markdown("---")
    st.header("💵 Pending Cash Collections")
    cash_orders = conn.execute("SELECT * FROM orders WHERE payment_method = 'Cash to Waiter' AND payment_status = 'Pending'").fetchall()
    
    if not cash_orders:
        st.success("No pending cash collections.")
    else:
        for order in cash_orders:
            st.error(f"**Order #{order['order_id']}** - Table {order['table_number']} | Amount: ₹{order['total_amount']}")
            if st.button(f"CASH RECEIVED ##{order['order_id']}"):
                conn.execute("UPDATE orders SET payment_status='Paid' WHERE order_id=?", (order['order_id'],))
                conn.commit()
                st.rerun()
                
    conn.close()


def page_admin():
    st.title("📊 ADMIN DASHBOARD")
    
    conn = get_db_connection()
    
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_sales = conn.execute("SELECT SUM(total_amount) FROM orders WHERE payment_status='Paid'").fetchone()[0] or 0
    pending_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE order_status != 'Delivered'").fetchone()[0]
    unpaid_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE payment_status = 'Pending'").fetchone()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Sales (Paid)", f"₹{total_sales}")
    col3.metric("Active Orders", pending_orders)
    col4.metric("Unpaid Orders", unpaid_orders)
    
    st.markdown("---")
    st.subheader("Recent Orders")
    df_orders = pd.read_sql("SELECT order_id, table_number, customer_name, total_amount, order_status, payment_status, timestamp FROM orders ORDER BY timestamp DESC LIMIT 20", conn)
    st.dataframe(df_orders, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Menu Management")
    
    df_menu = pd.read_sql("SELECT id, category, name, price, available FROM menu", conn)
    st.write("Edit prices or availability below (0 = Disabled, 1 = Enabled):")
    edited_menu = st.data_editor(df_menu, use_container_width=True, hide_index=True)
    
    if st.button("Save Menu Changes", type="primary"):
        for index, row in edited_menu.iterrows():
            conn.execute("UPDATE menu SET price=?, available=? WHERE id=?", (row['price'], row['available'], row['id']))
        conn.commit()
        st.success("Menu updated successfully!")
        
    conn.close()

# ==========================================
# 4. MAIN APPLICATION ROUTING
# ==========================================
def main():
    st.set_page_config(page_title="Smart Restaurant System", page_icon="🍽️", layout="wide")
    
    init_db()
    
    query_params = st.query_params
    
    if query_params.get("mode") == "customer":
        page_customer_flow()
    else:
        st.sidebar.title("Restaurant Management")
        role = st.sidebar.radio("Select View:", [
            "1. QR Generator (Customer Entry)",
            "2. Kitchen Dashboard",
            "3. Waiter Dashboard",
            "4. Admin Dashboard"
        ])
        
        st.sidebar.markdown("---")
        st.sidebar.info("Hackathon Note: To view customer UI exactly as phone users see it, scan the QR code or append `/?mode=customer` to the URL.")
        
        if role == "1. QR Generator (Customer Entry)":
            page_qr_generator()
        elif role == "2. Kitchen Dashboard":
            page_kitchen()
        elif role == "3. Waiter Dashboard":
            page_waiter()
        elif role == "4. Admin Dashboard":
            page_admin()

if __name__ == "__main__":
    main()