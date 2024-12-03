from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Product(Base):
    def __init__(self, db):
        self.db = db

    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    description = Column(String)
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

    def get_all_products(self):
        return self.db.query(Product).all()

    def get_product_by_name(self, session, name):
        return self.db.query(Product).filter_by(name=name).first()

    def get_product_by_id(self, session, product_id):
        return self.db.query(Product).filter_by(id=product_id).first()
