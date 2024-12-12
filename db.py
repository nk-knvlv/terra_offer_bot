from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from models.base import Base
from models.category import CategoryModel
from models.product import ProductModel
from models.cart_product import CartProductModel
from models.order import OrderModel
from dotenv import load_dotenv
from transliterate import translit
import os

from src.lang.ru import menu, food_category_names, drink_category_names


class DB:

    def __init__(self):
        self.connection = self.get_connection()

    @staticmethod
    def get_connection():
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def prepare(self):
        self.create_tables()

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

        self.fill_in()

    def fill_in(self):
        connection = self.get_connection()
        # Создаем несколько товаров при первом запуске
        if not connection.query(ProductModel).first():
            # Создание родительских категорий
            # Создание родительских категорий
            parent_category_food = CategoryModel(name="🍞 Еда")
            parent_category_drinks = CategoryModel(name="🍷 Напитки")

            # Сохранение родительских категорий в базу данных
            self.connection.add_all([parent_category_food, parent_category_drinks])
            self.connection.commit()  # Теперь у родительских категорий будут id

            # Запрос родительских категорий из базы данных
            parent_category_food = self.connection.query(CategoryModel).filter_by(name="🍞 Еда").first()
            parent_category_drinks = self.connection.query(CategoryModel).filter_by(name="🍷 Напитки").first()

            food_categories = []
            drink_categories = []
            for name in food_category_names:
                category = CategoryModel(name=name, parent=parent_category_food)
                food_categories.append(category)

            for name in drink_category_names:
                category = CategoryModel(name=name, parent=parent_category_drinks)
                drink_categories.append(category)
            # Сохранение дочерних категорий в базу данных
            self.connection.add_all([
                *food_categories,
                *drink_categories
            ])
            self.connection.commit()  # Теперь у дочерних категорий тоже будут id

            # Запрос дочерних категорий из базы данных
            categories_food = self.connection.query(CategoryModel).filter_by(parent=parent_category_food).all()
            categories_drinks = self.connection.query(CategoryModel).filter_by(parent=parent_category_drinks).all()

            product_models = []
            all_categories = menu['Напитки'].copy()
            all_categories.update(menu['Еда'])
            for category_name, products in all_categories.items():
                for product_name, product_fields in products.items():
                    product_model = ProductModel(
                        self,
                        name=product_name,
                        price=product_fields['price'],
                        category=next(
                            cat for cat in [*categories_food, *categories_drinks]
                            if category_name in cat.name),
                        description=product_fields['description'],
                        photo_path=f"src/images/{translit(
                            product_name.lower(),
                            'ru',
                            reversed=True).replace('\'', '').replace(' ', '_')}.jpg")
                    product_models.append(product_model)

            # Сохранение продуктов в базу данных
            self.connection.add_all(product_models)
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
    def test(self):
        products = self.connection.query(ProductModel).all()
        for product in products:
            print(f'{product.photo_path} - {product.category.name}')
