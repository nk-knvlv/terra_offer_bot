from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLAEnum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from models.cart_product import CartProductModel


class CartModel:
    def __init__(self, db):
        self.connection = db.connection

    def get_all(self, user_id):
        return self.connection.query(CartProductModel).filter_by(user_id=user_id).all()

    def get_product_by_id(self, user_id, product_id):
        return self.connection.query(CartProductModel).filter_by(user_id=user_id, product_id=product_id).first()

    def add_cart_product(self, user_id, product_id):
        cart_product = self.get_product_by_id(user_id, product_id)
        if cart_product:
            cart_product.quantity += 1
        else:
            cart_products = CartProductModel(username=user_id, product_id=product_id, quantity=1)
            self.connection.add(cart_products)
        self.connection.commit()

    def clear_cart(self, username):
        self.connection.query(CartProductModel).filter_by(username=username).delete()
        self.connection.commit()
