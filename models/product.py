from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class ProductModel(Base):
    def __init__(self, db):
        self.connection = db.connection

    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

    def get_all_products(self):
        return self.connection.query(ProductModel).all()

    def get_product_by_name(self, name):
        return self.connection.query(ProductModel).filter_by(name=name).first()

    def get_product_by_id(self, product_id):
        return self.connection.query(ProductModel).filter_by(id=product_id).first()