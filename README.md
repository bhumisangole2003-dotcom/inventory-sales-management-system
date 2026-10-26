# Inventory & Sales Management System

A web-based application built using Python, FastAPI, SQLAlchemy, and Streamlit to manage products, track inventory, record sales, and monitor business performance.

## 📌 Project Overview

The Inventory & Sales Management System helps businesses maintain product records, monitor stock levels, manage sales transactions, and identify products that need restocking. It provides a Streamlit dashboard and a FastAPI backend for inventory and sales operations.

## 🎯 Problem Statement

Managing inventory and sales manually can lead to incorrect stock records, overselling, difficulty tracking sales, and delays in identifying low-stock products.

This project provides a centralized application to simplify inventory management, automate stock updates after sales, and display useful sales information through a dashboard.

## 💡 Solution

The application combines a FastAPI backend with a Streamlit frontend. It uses a database to store product and sales information, validates transactions, updates inventory after sales, and presents sales metrics to the user.

## ✨ Features

- **Product Management:** Add, view, update, and delete product records.
- **Inventory Tracking:** Monitor available stock quantities.
- **Sales Management:** Record sales transactions.
- **Automatic Stock Updates:** Reduce stock after a successful sale.
- **Overselling Prevention:** Prevent sales that exceed available stock.
- **Low-Stock Alerts:** Identify products that need restocking.
- **Sales History:** View previously recorded sales.
- **CSV Export:** Download sales records for further analysis.
- **Dashboard:** Display revenue and top-selling products.
- **Login:** Supports the project's configured login functionality.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend REST API development |
| Streamlit | Interactive user interface and dashboard |
| SQLAlchemy | Database ORM and query management |
| Pydantic | Data validation and schemas |
| Uvicorn | ASGI server for running FastAPI |
| SQLite / PostgreSQL | Database, depending on configuration |

## 📦 Python Packages

The following packages support the application's main functionality. The actual installed dependencies are defined in `requirements.txt`.

| Package | Purpose |
|---|---|
| `fastapi` | Creates backend API endpoints |
| `uvicorn` | Runs the FastAPI server |
| `sqlalchemy` | Handles database operations |
| `pydantic` | Validates input data |
| `streamlit` | Creates the frontend and dashboard |
| `pandas` | Supports tabular data processing, if used |
| `psycopg2-binary` | PostgreSQL connectivity, if configured |

### Install the packages

From the project root directory, run:

```bash
pip install -r requirements.txt
```

To check the packages installed in your active Python environment:

```bash
pip list
```

## 📁 Project Structure

```text
inventory_sales_project/
│
├── backend/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: The structure above reflects the main files shown in the project. Keep it aligned with your actual repository.*

## ⚙️ Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/bhumisangole2003-dotcom/inventory-sales-management-system.git
```

### Step 2: Open the Project Directory

```bash
cd inventory-sales-management-system
```

### Step 3: Create a Virtual Environment (Optional)

```bash
python -m venv my_env
```

Activate it on Windows:

```bash
my_env\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ How to Run the Project

Run the backend and frontend in two separate VS Code terminals.

### Terminal 1: Start the FastAPI Backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

### Terminal 2: Start the Streamlit Frontend

From the project root directory, run:

```bash
cd frontend
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to use the application.

## 🗄️ Database Configuration

The application uses the database URL configured in `backend/database.py`.

- **SQLite:** Use the configured SQLite database for local development.
- **PostgreSQL:** To use PostgreSQL, configure the database connection URL and install the appropriate PostgreSQL driver.

For PostgreSQL, the driver can be installed with:

```bash
pip install psycopg2-binary
```

Ensure the database exists and the connection settings are correct before starting the backend.

## 🔄 Application Workflow

1. Open the Streamlit frontend.
2. Log in using the authentication functionality provided by the application.
3. Add or manage product information.
4. Record sales transactions.
5. The backend validates the transaction and updates stock.
6. Review low-stock alerts and sales information.
7. Export sales history when required.

## 🚀 Future Enhancements

- Dedicated supplier management
- Customer management
- Role-based access control
- Sales reports with date filters
- Profit analysis using product cost prices
- Advanced analytics and visualizations




