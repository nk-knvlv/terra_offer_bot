from models.enums import OrderFieldsLang, OrderStatus
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
from views.view import View


class OrderView(View):
    def __init__(self, order_controller, admin_controller):
        self.admin_controller = admin_controller
        self.order_controller = order_controller

    def get_order_view(self, order, user):
        order_date = f"{order.date.month:02}/{order.date.day:02} {order.date.hour:02}:{order.date.minute:02}"
        username = ''
        user_info = ''
        if self.admin_controller.is_admin(user.id):
            username = user.name
            excluded_fields = ['id', 'user_id', 'username', 'products', '_sa_instance_state', 'date', 'status']
            user_info = '\n' + "\n".join(
                f"{OrderFieldsLang[field].value.capitalize()}: {value}"
                for field, value in order.__dict__.items()
                if field not in excluded_fields
            )
            user_info += f'\nCтатус: {OrderStatus(order.status).value}'
        info_str = (f'{('Заказ ' + order_date + " " + username)}'
                    f'{user_info}'
                    )
        order_products = json.loads(order.products)
        products_str = "\n".join(
            f"{product_name}: {quantity} шт"
            for product_name, quantity in order_products.items()
        )

        order_view = (f'\n{info_str}\n '
                      f'{products_str}')


        return order_view

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user):
        keyboard = []
        orders = self.order_controller.get_all(user_id=user.id)

        query = update.callback_query
        # Формируем текст в виде таблицы с использованием HTML
        if orders:
            orders_view = f'{'Заказы'}'

            for order in orders:  # Пропускаем заголовок
                order_view = self.get_order_view(order, user)
                orders_view += '\n\n|==========================|\n' + order_view

        else:
            orders_view = 'Заказов нет'
        footer = self.get_footer(update, context)
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(orders_view, reply_markup=reply_markup)
