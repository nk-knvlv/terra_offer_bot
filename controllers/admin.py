from datetime import datetime

from models.enums import OrderFieldsLang
import json


class AdminController:
    def __init__(self, admin_id):
        self.admin_id = admin_id

    async def send_new_order_notice(self, order_details, context):
        # Создаем строку в формате "Ключ: Значение"
        excluded_keys = ['json_products', 'username']
        now = datetime.now()
        order_date = f"{now.month:02}/{now.day:02} - {now.hour:02}:{now.minute:02}"
        username = order_details['username']
        order_info = "\n".join(
            f"{OrderFieldsLang[key].value.capitalize()}: {value}" for key, value in order_details.items() if
            key not in excluded_keys)
        cart = (f'Корзина:\n' +
                '\n'.join([f"{product} - {quantity} шт"
                           for product, quantity in json.loads(order_details['json_products']).items()]))
        order_view = ('Новый заказ:\n'
                      f"{order_date} - {username}\n"
                      f"{order_info}\n\n"
                      f"{cart}\n"
                      )

        # Отправляем уведомление
        await context.bot.send_message(chat_id=self.admin_id,
                                       text=order_view)

    def is_admin(self, user_id):
        if user_id == self.admin_id:
            return True
        return False

    async def get_admin_nickname(self, update, context):
        user = await context.bot.get_chat(self.admin_id)
        nickname = user.username if user.username else "Нет никнейма"
        return f"@{nickname}"


