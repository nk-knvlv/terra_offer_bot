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

    def add_cart_product(self, user, product_id):
        cart_product = self.get_product_by_id(user.id, product_id)
        if cart_product:
            cart_product.quantity += 1
        else:
            cart_products = CartProductModel(user_id=user.id, username=user.username, product_id=product_id, quantity=1)
            self.connection.add(cart_products)
        self.connection.commit()

    def decrease_cart_product(self, user, product_id):
        cart_product = self.get_product_by_id(user.id, product_id)
        if cart_product:
            if cart_product.quantity > 1:
                cart_product.quantity -= 1
            else:
                self.connection.delete(cart_product)
            self.connection.commit()

    def clear_cart(self, user_id):
        self.connection.query(CartProductModel).filter_by(user_id=user_id).delete()
        self.connection.commit()

    def get_products_count(self, user_id):
        quantity = 0
        products = self.get_all(user_id)
        for product in products:
            quantity += product.quantity
        return quantity
