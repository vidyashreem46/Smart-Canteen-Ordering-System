# 🍽️ Smart Canteen Ordering System

A digital food ordering and order tracking system designed to reduce waiting time and improve the overall canteen ordering experience.

Customers can scan one common QR code, select their table, browse the digital menu, place orders, track order status, choose a payment method, and download a digital bill.

The system also includes separate workflows for the kitchen, waiter, and administrator.

---

## 📌 Project Overview

Traditional canteen ordering can involve long queues, manual order taking, order-status confusion, and manual bill generation.

The **Smart Canteen Ordering System** provides a simple digital workflow to make ordering and order management faster and more organized.

### Basic Workflow

```text
Customer
   ↓
Scan Common QR Code
   ↓
Select Table 1 / 2 / 3 / 4
   ↓
Enter Customer Name
   ↓
Browse Digital Menu
   ↓
Add Items to Cart
   ↓
Place Order
   ↓
Kitchen Receives Order
   ↓
Preparing
   ↓
Ready
   ↓
Customer Sees "Food Ready"
   ↓
Payment
   ↓
Digital Bill
   ↓
Waiter Delivers Food
   ↓
Delivered
```

---

## ✨ Features

### 👤 Customer

* One common QR code for the restaurant/canteen
* Select one of 4 tables
* Enter customer name
* Browse the digital menu
* Search food items
* Select item quantities
* View cart and grand total
* Place orders digitally
* Track order status
* Choose Online Payment or Cash to Waiter
* View payment status
* Download a digital bill
* Place another order

### 👨‍🍳 Kitchen

* View new and preparing orders
* View customer and table details
* View ordered food items
* Update order status:

```text
New → Preparing → Ready
```

### 🧑‍🍳 Waiter

* View food-ready orders
* See the table and customer for each order
* Mark orders as Delivered
* Manage pending cash collections

### 📊 Admin

* View total orders
* View total paid sales
* View active orders
* View unpaid orders
* View recent orders
* View menu items
* Edit food prices
* Enable or disable menu items

---

## 🪑 Table System

The project supports exactly **4 tables**:

* Table 1
* Table 2
* Table 3
* Table 4

Instead of creating a separate QR code for every table, the system uses **one common QR code**.

```text
              ONE COMMON QR
                    ↓
              Customer Scans
                    ↓
        Select Table 1 / 2 / 3 / 4
                    ↓
               Place Order
```

---

## 🍴 Menu Categories

The application contains the following menu categories:

* **Breakfast**
* **Main Course**
* **Snacks**
* **Chats**
* **Hot Beverages**
* **Cold Beverages**
* **Fresh Juices**
* **Desserts**

The menu includes items such as Idli, Vada, Dosa, Meals, Pulao, Fried Rice, Noodles, Samosa, Pani Puri, Tea, Coffee, Juices, Ice Cream, Brownie, and more.

---

## 🛠️ Technology Stack

| Technology | Purpose                  |
| ---------- | ------------------------ |
| Python     | Application development  |
| Streamlit  | Web-based user interface |
| SQLite     | Database management      |
| Pandas     | Data handling            |
| QRCode     | QR code generation       |
| Pillow     | Image processing         |

---

## 🗄️ Database

The application uses **SQLite** for local data storage.

The database contains:

### Menu

Stores:

* Food category
* Food name
* Price
* Availability

### Orders

Stores:

* Order ID
* Table number
* Customer name
* Total amount
* Order status
* Payment method
* Payment status
* Timestamp

### Order Items

Stores:

* Order ID
* Item name
* Quantity
* Price
* Subtotal

The local database file `canteen.db` is intentionally excluded from GitHub through `.gitignore`.

---

## 🔄 Order Status Flow

Each order moves through:

```text
NEW
 ↓
PREPARING
 ↓
READY
 ↓
DELIVERED
```

This allows the kitchen, waiter, and customer to follow the progress of an order.

---

## 💳 Payment

The system supports two payment methods:

* **Online Payment**
* **Cash to Waiter**

For online payment, the current project uses a **demo confirmation workflow** rather than a live payment gateway.

For cash payments, the waiter can mark the payment as received.

After payment is completed, the customer can view and download the digital bill.

---

## 📱 QR Code Access

The application generates a common QR code for customer access.

When the application is running on a local network, customers can scan the QR code from a phone connected to the same Wi-Fi network.

Example local URL:

```text
http://192.168.x.x:8501/?mode=customer
```

The exact IP address depends on the computer's local network.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/vidyashreem46/Smart-Canteen-Ordering-System.git
```

### 2. Open the project folder

```bash
cd Smart-Canteen-Ordering-System
```

### 3. Create a virtual environment (Optional)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📂 Project Structure

```text
Smart-Canteen-Ordering-System/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Main Files

**app.py**
Main Streamlit application containing the customer, kitchen, waiter, QR, and admin workflows.

**requirements.txt**
Contains the Python packages required to run the project.

**.gitignore**
Prevents files such as the local SQLite database and Python cache files from being uploaded to GitHub.

**README.md**
Project documentation and setup instructions.

---

## 👥 System Roles

```text
                 Smart Canteen
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
    Customer       Kitchen       Waiter
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                    Admin
```

### Customer

Places orders and tracks order status.

### Kitchen

Receives orders and updates preparation status.

### Waiter

Delivers ready orders and manages cash collections.

### Admin

Monitors orders, sales, and menu information.

---

## 🎯 Objectives

The main objectives of the project are:

1. Reduce customer waiting time.
2. Digitize the food ordering process.
3. Reduce manual order-taking errors.
4. Provide order status tracking.
5. Simplify bill generation.
6. Improve communication between customers and staff.
7. Provide centralized order and menu management.

---

## 🌍 Possible Use Cases

The system can be adapted for:

* College canteens
* School cafeterias
* Office cafeterias
* Company food courts
* Small restaurants
* Hotels
* Hospitals
* Workplace cafeterias

---

## 🔮 Future Enhancements

Possible future improvements include:

* User authentication and role-based access
* Real payment gateway integration
* Dedicated daily sales reports
* Advanced sales analytics
* Customer order history
* Email/SMS notifications
* WhatsApp notifications
* Inventory management
* Food stock tracking
* Cloud database integration
* Mobile application
* Multiple canteen or branch support

---

## 🏆 Hackathon Project

This project was developed as part of a college hackathon software development challenge.

### Problem Statement

**Smart Canteen Ordering System**

The objective was to design a software system that enables:

* Digital menu display
* Online order placement
* Bill generation
* Order status tracking
* Sales monitoring

The project was developed as a functional prototype within the hackathon development time.

---

## 📸 Project Screenshots

Screenshots can be added here to demonstrate:

* Common QR code
* Customer menu
* Cart and order placement
* Order tracking
* Kitchen dashboard
* Waiter dashboard
* Admin dashboard
* Digital bill

---

## 👩‍💻 Developer

**Vidyashree.M**

B.Sc. (Hons) Data Science and Artificial Intelligence

Sarada Vilas College

---

## 📄 License

This project is created for educational and demonstration purposes.
