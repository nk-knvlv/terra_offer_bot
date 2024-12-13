from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from models.enums import OrderFieldsLang
import json


class AdminController:
    def __init__(self, admin_id):
        self.admin_id = admin_id

    async def send_admin_new_order_notice(self, order_details, context):
        # Создаем строку в формате "Ключ: Значение"
        excluded_keys = ['json_products', 'username', 'label', 'id']
        now = datetime.now()
        order_time = f"{now.hour:02}:{now.minute:02}"
        username = order_details['username']
        order_info = "\n".join(
            f"{OrderFieldsLang[key].value.capitalize()}: {value}" for key, value in order_details.items() if
            key not in excluded_keys)
        cart = (f'Корзина:\n' +
                '\n'.join([f"{product} - {quantity} шт"
                           for product, quantity in json.loads(order_details['json_products']).items()]))
        order_view = ('Новый заказ:\n'
                      f"{order_details['label']} - {username} - {order_time}\n"
                      f"{order_info}\n\n"
                      f"{cart}\n"
                      )
        keyboard = []
        confirm_button = InlineKeyboardButton('✔️ Подтвердить',
                                              callback_data=f'orders-confirm-{order_details['id']}')
        cancel_button = InlineKeyboardButton('❌ Отменить', callback_data=f'orders-cancel-{order_details['id']}')
        view_order_button = InlineKeyboardButton('📝 К заказу',
                                                 callback_data=f'orders-view-{order_details['id']}')
        keyboard.append([view_order_button, cancel_button, confirm_button])

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # Отправляем уведомление
        await context.bot.send_message(chat_id=self.admin_id,
                                       text=order_view, reply_markup=reply_markup)

    def is_admin(self, user_id):
        if user_id == self.admin_id:
            return True
        return False

    async def get_admin_nickname(self, context):
        user = await context.bot.get_chat(self.admin_id)
        nickname = user.username if user.username else "Нет никнейма"
        return f"@{nickname}"

    @staticmethod
    async def send_user_notification(update, context, message, markup, user_id):
        await context.bot.send_message(chat_id=user_id,
                                       text=message, reply_markup=markup)
