class HelpView:

    def __init__(self):
        pass

    @staticmethod
    async def show(update, context):
        help_view = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это меню помощи\n"
            "/menu - Показать каталог товаров\n"
            "/cart - Показать содержимое вашей корзины\n"
            "Просто отправьте название товара, чтобы добавить его в корзину."
        )
        await update.message.reply_text(help_view)
