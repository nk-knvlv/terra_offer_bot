from models.enums import OrderFieldsLang
import json


class AdminController:
    def __init__(self, admin_id):
        self.admin_id = admin_id

    async def send_new_order_notice(self, order_details, context):
        # Создаем строку в формате "Ключ: Значение"
        excluded_keys = ['json_products', 'user']
        order_view = f"{order_details['user'].name}" + "\n".join(
            f"{OrderFieldsLang[key].value.capitalize()}: {value}" for key, value in order_details.items() if
            key not in excluded_keys)+'\n'
        order_view += f'Корзина:\n' + '\n'.join(json.loads(order_details['json_products']))
        # Отправляем уведомление
        await context.bot.send_message(chat_id=self.admin_id,
                                       text=f"Новый заказ:\n{order_view}")

    def is_admin(self, user):
        if user.id == self.admin_id:
            return True
        return False
