from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from models.product import Product
from models.category import Category
from dotenv import load_dotenv
import os

Base = declarative_base()


class DB:

    def __init__(self):
        self.session = self.get_session()
        self.create_tables()

    @staticmethod
    def get_session():
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def create_tables(self):
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

        self.first_fill_in(self.session)

    def first_fill_in(self, session):
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

    def main_fill_in(self):
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
