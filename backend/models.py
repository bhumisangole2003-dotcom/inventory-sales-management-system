from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, default="General")
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=5)  # below this = "low stock"

    sales = relationship("Sale", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # price at time of sale
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="sales")

    @property
    def product_name(self):
        return self.product.name


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # never store plain passwords
    created_at = Column(DateTime, default=datetime.now)


class AuthToken(Base):
    """One row per logged-in session. Deleting the row = logout."""
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User")
