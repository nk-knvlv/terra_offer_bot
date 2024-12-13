from models.enums import OrderFieldsLang, OrderStatus
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import json
from views.view import View


class OrderView(View):
    def __init__(self, order_controller, admin_controller, navigation_controller):
        self.admin_controller = admin_controller
        self.order_controller = order_controller
        self.navigation_controller = navigation_controller

    def get_order_info(self, order, user):
        order_label = order.label
        order_date = f"{order.date.month:02}/{order.date.day:02} {order.date.hour:02}:{order.date.minute:02}"
        status_info = f'\nCтатус: {OrderStatus(order.status).value}'
        username = ''
        user_info = ''
        if self.admin_controller.is_admin(user.id):
            username = user.name
            excluded_fields = [
                'id',
                'user_id',
                'username',
                'products',
                '_sa_instance_state',
                'date',
                'status',
                'label'
            ]
            user_info = '\n' + "\n".join(
                f"{OrderFieldsLang[field].value.capitalize()}: {value}"
                for field, value in order.__dict__.items()
                if field not in excluded_fields
            )
        order_products = json.loads(order.products)
        products_str = "\n".join(
            f"{product_name}: {quantity} шт"
            for product_name, quantity in order_products.items()
        )
        order_view = (f'{(order_label + " " + order_date + " " + username)}\n'
                      f'{user_info}'
                      f'{products_str}'
                      f'{status_info}'
                      )
        return order_view

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        user = update.callback_query.from_user
        if 'order_id' in context.user_data and context.user_data['order_id']:
            order_id = context.user_data['order_id']
            order = self.order_controller.get_order_by_id(order_id)
            order_info = self.get_order_info(order, user)

            if self.admin_controller.is_admin(user_id=user.id):
                order_confirmation_buttons = self.get_order_confirmation_buttons(order)
                keyboard.append(order_confirmation_buttons)
        else:
            orders = self.order_controller.get_all(user_id=user.id)
            if orders:
                order_info = f'{'Заказы'}'
                for order in orders:
                    order_buttons = self.get_order_info_button(order, user)
                    keyboard.append([order_buttons])
            else:
                order_info = 'Заказов нет'

        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(order_info, reply_markup=reply_markup)

    def get_order_info_button(self, order, user):
        order_date = f"{order.date.month:02}/{order.date.day:02} {order.date.hour:02}:{order.date.minute:02}"
        username = ''
        if self.admin_controller.is_admin(user.id):
            username = f" {user.name}"
        order_info = f"{order.label}{username} {order_date}"
        view_order_button = InlineKeyboardButton(order_info, callback_data=f'view-order-{order.id}')
        return view_order_button

    @staticmethod
    def get_order_confirmation_buttons(order):
        confirm_button = InlineKeyboardButton('✔️ Подтвердить', callback_data=f'action-order-confirm-{order.id}')
        cancel_button = InlineKeyboardButton('❌ Отменить', callback_data=f'action-order-cancel-{order.id}')
        return [cancel_button, confirm_button]
