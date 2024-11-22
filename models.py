from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class CartProduct(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    product = relationship("Product")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    # Связь с дочерними категориями
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")

    # Связь с родительской категорией
    parent = relationship("Category", remote_side=[id], back_populates="children")
    # Связь с продуктами
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
