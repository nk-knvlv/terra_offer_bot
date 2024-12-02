from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from models import Base, Product, CartProduct, Category, Order, OrderStatus
from dotenv import load_dotenv
from datetime import datetime
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


def get_all_cart_products(session, username):
    return session.query(CartProduct).filter_by(username=username).all()


def get_product_by_name(session, name):
    return session.query(Product).filter_by(name=name).first()


def get_product_by_id(session, product_id):
    return session.query(Product).filter_by(id=product_id).first()


def get_cart_product(session, username, product_id):
    return session.query(CartProduct).filter_by(username=username, product_id=product_id).first()


def add_cart_product(session, username, product_id, quantity):
    cart_products = CartProduct(username=username, product_id=product_id, quantity=quantity)
    session.add(cart_products)
    session.commit()


def clear_cart(session, user_id):
    session.query(CartProduct).filter_by(user_id=user_id).delete()
    session.commit()


def first_fill_in(session):
    # Создаем несколько товаров при первом запуске
    if not session.query(Product).first():
        # Создание родительских категорий
        parent_category_food = Category(name="Еда")
        parent_category_drinks = Category(name="Напитки")

        # Создание подкатегорий для еды
        category_breakfasts = Category(name="Завтраки", parent=parent_category_food)
        category_snacks = Category(name="Закуски", parent=parent_category_food)
        category_salads = Category(name="Салаты", parent=parent_category_food)
        category_soups = Category(name="Супы", parent=parent_category_food)
        category_pasta = Category(name="Паста", parent=parent_category_food)
        category_hot_dishes = Category(name="Горячее", parent=parent_category_food)
        category_pizza = Category(name="Пицца", parent=parent_category_food)
        category_desserts = Category(name="Десерты", parent=parent_category_food)
        category_additional = Category(name="Дополнительно", parent=parent_category_food)

        # Создание подкатегорий для напитков
        category_tea = Category(name="Чай", parent=parent_category_drinks)
        category_coffee = Category(name="Кофе", parent=parent_category_drinks)
        category_fruit_tea = Category(name="Фруктовый чай", parent=parent_category_drinks)
        category_lemonades = Category(name="Лимонады", parent=parent_category_drinks)
        category_milkshakes = Category(name="Милкшейки", parent=parent_category_drinks)
        category_water = Category(name="Вода", parent=parent_category_drinks)

        # Создание продуктов
        product_fettuccine = Product(name="Феттучини Альфредо", price=700, category=category_pasta)
        product_pepperoni_pizza = Product(name="Пицца Пепперони", price=800, category=category_pizza)
        product_coffee_cappuccino = Product(name="Капучино", price=330, category=category_pizza)

        # Собираем все сущности в список
        categories = [
            parent_category_food,
            parent_category_drinks,
            category_breakfasts,
            category_snacks,
            category_salads,
            category_soups,
            category_pasta,
            category_hot_dishes,
            category_pizza,
            category_desserts,
            category_additional,
            category_tea,
            category_coffee,
            category_fruit_tea,
            category_lemonades,
            category_milkshakes,
            category_water
        ]

        products = [
            product_fettuccine,
            product_pepperoni_pizza,
            product_coffee_cappuccino
        ]

        session.add_all([
            *categories,
            *products
        ])
        session.commit()


def main_fill_in():
    # Пример создания категорий и продуктов
    parent_category_food = Category(name="Еда")
    category_pasta = Category(name="Паста", parent=parent_category_food)
    category_pizza = Category(name="Пицца", parent=parent_category_food)

    parent_category_drinks = Category(name="Напитки")
    category_coffee = Category(name="Кофе", parent=parent_category_drinks)
    category_lemonade = Category(name="Лимонады", parent=parent_category_drinks)

    product_fettuccine = Product(name="Феттучини Альфредо", price=700, category=category_pasta)
    product_pepperoni_pizza = Product(name="Пицца Пепперони", price=800, category=category_pizza)

    # session.commit()


def add_order(session, username: str, phone: str, address: str, comment: str, json_products: str):
    order = Order(
        username=username,
        phone=phone,
        address=address,
        comment=comment,
        products=json_products,
        date=datetime.now(),
        status=OrderStatus.PROCESSING
    )
    session.add(order)
    session.commit()
    return order


def get_user_orders(session, username):
    return session.query(Order).filter_by(username=username).all()


def get_all_orders(session):
    return session.query(Order).all()
