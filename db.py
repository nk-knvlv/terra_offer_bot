from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from models.base import Base
from models.category import CategoryModel
from models.product import ProductModel
from models.cart_product import CartProductModel
from models.order import OrderModel
from dotenv import load_dotenv
import os


class DB:

    def __init__(self):
        self.prepare()
        self.connection = self.get_connection()

    @staticmethod
    def get_connection():
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    async def prepare(self):
        await self.create_tables()

    async def create_tables(self):
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)

        # Создаем таблицы
        await Base.metadata.create_all(engine)

        # Проверка таблиц
        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            for row in result:
                print(row)

        self.first_fill_in()

    def first_fill_in(self):
        connection = self.get_connection()
        # Создаем несколько товаров при первом запуске
        if not connection.query(ProductModel).first():
            # Создание родительских категорий
            parent_category_food = CategoryModel(name="Еда")
            parent_category_drinks = CategoryModel(name="Напитки")

            # Создание подкатегорий для еды
            category_breakfasts = CategoryModel(name="Завтраки", parent=parent_category_food)
            category_snacks = CategoryModel(name="Закуски", parent=parent_category_food)
            category_salads = CategoryModel(name="Салаты", parent=parent_category_food)
            category_soups = CategoryModel(name="Супы", parent=parent_category_food)
            category_pasta = CategoryModel(name="Паста", parent=parent_category_food)
            category_hot_dishes = CategoryModel(name="Горячее", parent=parent_category_food)
            category_pizza = CategoryModel(name="Пицца", parent=parent_category_food)
            category_desserts = CategoryModel(name="Десерты", parent=parent_category_food)
            category_additional = CategoryModel(name="Дополнительно", parent=parent_category_food)

            # Создание подкатегорий для напитков
            category_tea = CategoryModel(name="Чай", parent=parent_category_drinks)
            category_coffee = CategoryModel(name="Кофе", parent=parent_category_drinks)
            category_fruit_tea = CategoryModel(name="Фруктовый чай", parent=parent_category_drinks)
            category_lemonades = CategoryModel(name="Лимонады", parent=parent_category_drinks)
            category_milkshakes = CategoryModel(name="Милкшейки", parent=parent_category_drinks)
            category_water = CategoryModel(name="Вода", parent=parent_category_drinks)

            # Создание продуктов
            product_fettuccine = ProductModel(name="Феттучини Альфредо", price=700, category=category_pasta)
            product_pepperoni_pizza = ProductModel(name="Пицца Пепперони", price=800, category=category_pizza)
            product_coffee_cappuccino = ProductModel(name="Капучино", price=330, category=category_pizza)

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

            self.connection.add_all([
                *categories,
                *products
            ])
            self.connection.commit()
    #
    # def main_fill_in(self):
    #     # Пример создания категорий и продуктов
    #     parent_category_food = CategoryModel(name="Еда")
    #     category_pasta = CategoryModel(name="Паста", parent=parent_category_food)
    #     category_pizza = CategoryModel(name="Пицца", parent=parent_category_food)
    #
    #     parent_category_drinks = CategoryModel(name="Напитки")
    #     category_coffee = CategoryModel(name="Кофе", parent=parent_category_drinks)
    #     category_lemonade = CategoryModel(name="Лимонады", parent=parent_category_drinks)
    #
    #     product_fettuccine = ProductModel(name="Феттучини Альфредо", price=700, category=category_pasta)
    #     product_pepperoni_pizza = ProductModel(name="Пицца Пепперони", price=800, category=category_pizza)
    #
    #     # session.commit()
