from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from models.base import Base


class ProductModel(Base):
    def __init__(self, db, name=None, price=None, category=None):
        self.connection = db.connection
        self.name = name
        self.price = price
        self.category = category

    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)
    category = relationship("CategoryModel", back_populates="products")
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

    def get_all_products(self):
        return self.connection.query(ProductModel).all()

    def get_product_by_name(self, name):
        return self.connection.query(ProductModel).filter_by(name=name).first()

    def get_product_by_id(self, product_id):
        return self.connection.query(ProductModel).filter_by(id=product_id).first()
