from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from models.enums import OrderStatus
from datetime import datetime
from models.base import Base


class OrderModel(Base):

    def __init__(self, db):
        self.connection = db.connection

    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)  # Поле для хранения даты и времени
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    status = Column(SQLAEnum(OrderStatus), nullable=False)  # Используем SQLAlchemy enum
    products = Column(JSON)

    def __repr__(self):
        return f"<OrderModel(id={self.id}, username={self.username})>"

    def add_order(self, order):
        self.connection.add(order)
        self.connection.commit()
        return order

    def get_user_orders(self, user_id):
        return self.connection.query(OrderModel).filter_by(user_id=user_id).all()

    def get_all(self):
        return self.connection.query(OrderModel).all()
