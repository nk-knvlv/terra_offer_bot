from models.cart import CartModel
from telegram import InlineKeyboardButton


class CartController:
    def __init__(self, cart_model: CartModel, product_model):
        self.product_model = product_model
        self.cart_model = cart_model

    def get_products(self, user_id):
        return self.cart_model.get_all(user_id)

    async def add_product(self, update, context, product_id):
        user = update.callback_query.from_user
        self.cart_model.add_cart_product(product_id=product_id, user=user)

    async def decrease_product(self, update, context, product_id):
        user = update.callback_query.from_user
        self.cart_model.decrease_cart_product(product_id=product_id, user=user)

    def get_cart_product_by_id(self, user_id, product_id):
        return self.cart_model.get_product_by_id(user_id=user_id, product_id=product_id)

    def get_products_count(self, user_id):
        return self.cart_model.get_products_count(user_id=user_id)

    def get_cart_button(self, user_id):
        cart_products_count = self.get_products_count(user_id=user_id)
        cart_products_count_str = ''
        if cart_products_count:
            cart_products_count_str = f' ({cart_products_count})'
        cart_button = InlineKeyboardButton(
            text=f'🛒{cart_products_count_str}',
            callback_data=f"cart"
        )
        return cart_button

    def clear(self, user_id):
        self.cart_model.clear_cart(user_id=user_id)
