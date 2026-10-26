# Inventory & Sales Management (FastAPI + Streamlit)

## Setup
```bash
pip install -r requirements.txt
```

## Run (two terminals)
Terminal 1 - backend:
```bash
cd backend
uvicorn main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Terminal 2 - frontend:
```bash
cd frontend
streamlit run app.py
```

## Features
- Add / edit / delete products
- Record sales (stock reduces automatically, blocks overselling)
- Low-stock alerts, revenue, top products
- Sales history with CSV download

## Switch to PostgreSQL
In `backend/database.py` change DATABASE_URL to your PostgreSQL URL
and `pip install psycopg2-binary`.

## Ideas to extend
Customers table, categories table, login, date filters, profit (add cost price).
