from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum

Base = declarative_base()


class OrderStatus(Enum):
    PROCESSING = "В обработке"  # Заказ отправлен и находится в обработке
    PREPARING = "Готовится"  # Заказ готовится
    DELIVERY = "В доставке"  # Заказ доставляется
    COMPLETED = "Завершен"  # Заказ завершен


class OrderFieldsLang(Enum):
    phone = "номер"  # Заказ отправлен и находится в обработке
    comment = "комментарий"  # Заказ готовится
    address = "адрес"  # Заказ доставляется
    status = "статус"  # Заказ завершен


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    description = Column(String)
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)  # Поле для хранения даты и времени
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    status = Column(SQLAEnum(OrderStatus), nullable=False)  # Используем SQLAlchemy enum
    products = Column(JSON)

    def __repr__(self):
        return f"<Order(id={self.id}, username={self.username})>"


class CartProduct(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
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
