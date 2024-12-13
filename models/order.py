import string
from random import choices

from sqlalchemy import Column, Integer, String, JSON, Enum as SQLAEnum, DateTime
from models.enums import OrderStatus
from datetime import datetime
from models.base import Base


class OrderModel(Base):

    def __init__(
            self,
            db=None,
            user_id=None,
            username=None,
            phone=None,
            address=None,
            comment=None,
            products=None
    ):
        if db:
            self.connection = db.connection
        if username:
            self.username = username
        if phone:
            self.phone = phone
        if address:
            self.address = address
        if comment:
            self.comment = comment
        if products:
            self.products = products
        if user_id:
            self.user_id = user_id
            self.label = self.generate_unique_label()

        self.status = OrderStatus.PROCESSING
        self.date = datetime.now()

    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    label = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)  # Поле для хранения даты и времени
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    status = Column(SQLAEnum(OrderStatus), nullable=False)  # Используем SQLAlchemy enum
    products = Column(JSON)

    def __repr__(self):
        return f"<OrderModel(id={self.id}, username={self.username})>"

    async def add(self, order):
        self.connection.add(order)
        self.connection.commit()
        new_order = self.get_last_user_order(order.user_id)
        return new_order

    def get_user_orders(self, user_id):
        return self.connection.query(OrderModel).filter_by(user_id=user_id).all()

    def get_last_user_order(self, user_id):
        return self.connection.query(OrderModel).filter_by(user_id=user_id).first()

    def get_all(self):
        return self.connection.query(OrderModel).all()

    @staticmethod
    def generate_unique_label():
        letters = choices(string.ascii_uppercase, k=2)  # Выбор двух случайных букв
        numbers = choices(string.digits, k=2)
        return ''.join([letters[0], numbers[0], letters[1], numbers[1]])

    def change_order_status(self, order_id, new_status):
        new_status = OrderStatus[new_status]
        self.connection.query(OrderModel).filter_by(id=order_id).update({"status": new_status})
        self.connection.commit()

    def get_order_by_id(self, order_id):
        return self.connection.query(OrderModel).filter_by(id=order_id).first()
