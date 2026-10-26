from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from auth import (bearer, get_current_user, hash_password,
                  issue_token, verify_password)
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)  # creates tables on first run

app = FastAPI(title="Inventory & Sales API")


@app.get("/")
def root():
    return {"message": "Inventory & Sales API is running. Docs at /docs"}


# ---------------- AUTH ----------------
@app.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    username = data.username.strip().lower()
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(400, "Username already taken")
    user = models.User(username=username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": issue_token(db, user), "username": user.username}  # auto-login


@app.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username.strip().lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Wrong username or password")
    return {"token": issue_token(db, user), "username": user.username}


@app.post("/logout")
def logout(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if creds:
        db.query(models.AuthToken).filter(models.AuthToken.token == creds.credentials).delete()
        db.commit()
    return {"message": "Logged out"}


# ---------------- PRODUCTS ----------------
@app.post("/products", response_model=schemas.ProductOut, status_code=201, dependencies=[Depends(get_current_user)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    if db.query(models.Product).filter(models.Product.name == product.name).first():
        raise HTTPException(400, "A product with this name already exists")
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=list[schemas.ProductOut], dependencies=[Depends(get_current_user)])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).order_by(models.Product.id).all()


@app.put("/products/{product_id}", response_model=schemas.ProductOut, dependencies=[Depends(get_current_user)])
def update_product(product_id: int, data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", dependencies=[Depends(get_current_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if product.sales:
        raise HTTPException(400, "Cannot delete a product that has sales records")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


# ---------------- SALES ----------------
@app.post("/sales", response_model=schemas.SaleOut, status_code=201, dependencies=[Depends(get_current_user)])
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    product = db.get(models.Product, sale.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if sale.quantity > product.stock:
        raise HTTPException(400, f"Only {product.stock} units in stock")

    product.stock -= sale.quantity  # reduce inventory
    record = models.Sale(
        product_id=product.id,
        quantity=sale.quantity,
        unit_price=product.price,
        total=product.price * sale.quantity,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/sales", response_model=list[schemas.SaleOut], dependencies=[Depends(get_current_user)])
def list_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).order_by(models.Sale.id.desc()).all()


# ---------------- DASHBOARD ----------------
@app.get("/dashboard", dependencies=[Depends(get_current_user)])
def dashboard(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    total_revenue = db.query(func.coalesce(func.sum(models.Sale.total), 0)).scalar()
    total_sales = db.query(func.count(models.Sale.id)).scalar()

    top = (
        db.query(models.Product.name, func.sum(models.Sale.total).label("revenue"))
        .join(models.Sale)
        .group_by(models.Product.name)
        .order_by(func.sum(models.Sale.total).desc())
        .limit(5)
        .all()
    )
    return {
        "total_products": len(products),
        "total_units_in_stock": sum(p.stock for p in products),
        "low_stock": [
            {"name": p.name, "stock": p.stock, "reorder_level": p.reorder_level}
            for p in products if p.stock <= p.reorder_level
        ],
        "total_sales": total_sales,
        "total_revenue": round(total_revenue, 2),
        "top_products": [{"name": n, "revenue": round(r, 2)} for n, r in top],
    }
