from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from models import Item, CartItem
from dotenv import load_dotenv
import os


def prepare():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
    #
    # # Очистка таблиц
    # with engine.connect() as connection:
    #     session.query(Item).delete()
    #     session.query(CartItem).delete()
    #     # connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    #     # connection.execute(text("DELETE FROM cart_items"))
    #     # connection.execute(text("DELETE FROM items"))
    #
    # Base.metadata.create_all(engine)
    #
    # #db test
    #
    #
    # # Создаем новый товар
    # new_item = Item(name="Sample Item", price=19.99)
    # session.add(new_item)
    # session.commit()
    # #
    # item = session.query(Item).filter_by(name="Sample Item").first()
    # print(item.name, item.price)


def get_all_items(session):
    return session.query(Item).all()


def get_all_cart_items(session, user_id):
    return session.query(CartItem).filter_by(user_id=user_id).all()


def get_item_by_name(session, name):
    return session.query(Item).filter_by(name=name).first()


def get_cart_item(session, user_id, item_id):
    return session.query(CartItem).filter_by(user_id=user_id, item_id=item_id).first()


def add_cart_item(session, user_id, item_id, quantity):
    cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=quantity)
    session.add(cart_item)
    session.commit()


def clear_cart(session, user_id):
    session.query(CartItem).filter_by(user_id=user_id).delete()
    session.commit()


def first_fill_in(session):
    # Создаем несколько товаров при первом запуске
    if not session.query(Item).first():
        session.add_all([
            Item(name="Сервер", price=100.0),
            Item(name="Облако", price=150.0),
            Item(name="Amvera", price=200.0)
        ])
        session.commit()
