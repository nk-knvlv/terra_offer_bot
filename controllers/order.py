from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from models.order import OrderModel


class OrderController:
    def __init__(self, order_model, admin_controller):
        self.order_model = order_model
        self.admin_controller = admin_controller

    async def add(self, user, phone: str, address: str, comment: str, json_products: str):
        order = OrderModel(
            user_id=user.id,
            username=user.name,
            phone=phone,
            address=address,
            comment=comment,
            products=json_products,
        )
        return await self.order_model.add(order)

    def get_all(self, user_id):
        if self.admin_controller.is_admin(user_id=user_id):
            orders = self.order_model.get_all()
        else:
            orders = self.order_model.get_user_orders(user_id)
        return orders

    def get_user_orders(self, user_id):
        return self.order_model.get_user_orders(user_id=user_id)

    async def confirm(self, update, context, order_id):
        order = self.order_model.get_order_by_id(order_id)
        user_id = order.user_id
        order_label = order.label
        keyboard = []
        message = '\n'.join([
            f'🔔 Уведомление о заказе',
            f'Ваш заказ {order_label} подтвержден!',
            'Скоро курьер отправится к вам. 🛵💨',
            'Приятного аппетита! 🍽️✨'
        ])
        view_order_button = InlineKeyboardButton('📝 К заказу',
                                                 callback_data=f'view-order-{order_id}')
        keyboard.append([view_order_button])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await self.admin_controller.send_user_notification(
            update=update,
            context=context,
            message=message,
            user_id=user_id,
            markup=markup)
        self.order_model.change_order_status(order_id, 'CONFIRMED')

    async def cancel(self, update, context, order_id):
        order = self.order_model.get_order_by_id(order_id)
        user_id = order.user_id
        order_label = order.label
        keyboard = []
        message = '\n'.join([
            f"🔔 Уведомление о заказе",
            f"К сожалению, ваш заказ {order_label} был отменен.",
            f" Мы приносим свои извинения за неудобства.",
            "В ближайшее время с вами свяжется наш сотрудник.",
            "Если вы не получили ответа в течение 20 минут,",
            "пожалуйста, позвоните нам по телефону: +79637707161."])
        view_order_button = InlineKeyboardButton('📝 К заказу',
                                                 callback_data=f'view-order-{order_id}')
        keyboard.append([view_order_button])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await self.admin_controller.send_user_notification(

            update=update,
            context=context,
            message=message,
            user_id=user_id,
            markup=markup)
        self.order_model.change_order_status(order_id, 'CANCELLED')


def get_order_by_id(self, order_id):
    return self.order_model.get_order_by_id(order_id=order_id)
