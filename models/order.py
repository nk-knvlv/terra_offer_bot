from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from enums import OrderStatus
from datetime import datetime

Base = declarative_base()


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

    def add_order(self, username: str, phone: str, address: str, comment: str, json_products: str):
        order = Order(
            username=username,
            phone=phone,
            address=address,
            comment=comment,
            products=json_products,
            date=datetime.now(),
            status=OrderStatus.PROCESSING
        )
        self.db.add(order)
        self.db.commit()
        return order

    def get_user_orders(self, username):
        return self.db.query(Order).filter_by(username=username).all()

    def get_all_orders(self):
        return self.db.query(Order).all()
