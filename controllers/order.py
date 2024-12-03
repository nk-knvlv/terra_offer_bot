from datetime import datetime
from models.order import OrderModel
from models.enums import OrderStatus


class OrderController:
    def __init__(self, order_model, admin_controller):
        self.order_model = order_model
        self.admin_controller = admin_controller

    def new_order_admin_notice(self, order):
        self.admin_controller.send_new_order_notice(order)

    def add_order(self, username: str, phone: str, address: str, comment: str, json_products: str):
        order = OrderModel(
            username=username,
            phone=phone,
            address=address,
            comment=comment,
            products=json_products,
            date=datetime.now(),
            status=OrderStatus.PROCESSING
        )
        self.order_model.add_order(order)

    def get_all(self, user_id):
        if self.admin_controller.is_admin(user_id=user_id):
            orders = self.order_model.get_all()
        else:
            orders = self.order_model.get_user_orders(user_id)
        return orders

    def get_user_orders(self, user_id):
        return self.order_model.get_user_orders(user_id=user_id)
