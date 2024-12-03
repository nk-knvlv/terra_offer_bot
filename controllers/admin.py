class AdminController:
    def __init__(self, bot, admin_id):
        self.bot = bot
        self.admin_id = admin_id

    async def send_new_order_notice(self, order):
        # Создаем строку в формате "Ключ: Значение"
        order_view = get_order_view(order, user_id=self.admin_id)
        # order_view = "\n".join(f"{key.capitalize()}: {value}" for key, value in order_details.items())

        # Отправляем уведомление
        await self.bot.send_message(chat_id=self.admin_id,
                                       text=f"Новый заказ:\n{order_view}")

    def is_admin(self, user_id):
        if user_id == self.admin_id:
            return True
        return False
