from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class CartProduct(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    product = relationship("Product")

    def get_all(self, username):
        return self.db.query(CartProduct).filter_by(username=username).all()

    def get_product_by_id(self, username, product_id):
        return self.db.query(CartProduct).filter_by(username=username, product_id=product_id).first()

    def add_cart_product(self, username, product_id, quantity):
        cart_products = CartProduct(username=username, product_id=product_id, quantity=quantity)
        self.db.add(cart_products)
        self.db.commit()

    def clear_cart(self, user_id):
        self.db.query(CartProduct).filter_by(user_id=user_id).delete()
        self.db.commit()
