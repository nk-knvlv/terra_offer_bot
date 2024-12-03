from models.cart import CartModel


class CartController:
    def __init__(self, cart_model: CartModel, product_model):
        self.product_model = product_model
        self.cart_model = cart_model

    async def get_all_products(self, user_id):
        return self.cart_model.get_all(user_id)

    async def add_product(self, product_id, user_id):
        self.cart_model.add_cart_product(product_id=product_id, user_id=user_id)

    def get_cart_product_by_id(self, user_id, product_id):
        self.cart_model.get_product_by_id(user_id=user_id, product_id=product_id)
