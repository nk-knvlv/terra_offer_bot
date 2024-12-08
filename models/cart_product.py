from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from models.base import Base


class CartProductModel(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship("ProductModel")
