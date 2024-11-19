from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from models import Base, Product, CartProduct
from dotenv import load_dotenv
import os


def get_session():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def prepare():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)

    # Создаем таблицы
    Base.metadata.create_all(engine)

    # Проверка таблиц
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        for row in result:
            print(row)

    Session = sessionmaker(bind=engine)
    session = Session()

    first_fill_in(session)


def get_all_products(session):
    return session.query(Product).all()


def get_all_cart_products(session, user_id):
    return session.query(CartProduct).filter_by(user_id=user_id).all()


def get_product_by_name(session, name):
    return session.query(Product).filter_by(name=name).first()


def get_cart_product(session, user_id, products_id):
    return session.query(CartProduct).filter_by(user_id=user_id, products_id=products_id).first()


def add_cart_product(session, user_id, products_id, quantity):
    cart_products = CartProduct(user_id=user_id, products_id=products_id, quantity=quantity)
    session.add(cart_products)
    session.commit()


def clear_cart(session, user_id):
    session.query(CartProduct).filter_by(user_id=user_id).delete()
    session.commit()


def first_fill_in(session):
    # Создаем несколько товаров при первом запуске
    if not session.query(Product).first():
        session.add_all([
            Product(name="Сервер", price=100.0),
            Product(name="Облако", price=150.0),
            Product(name="Amvera", price=200.0)
        ])
        session.commit()
