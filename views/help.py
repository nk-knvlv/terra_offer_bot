class HelpView:

    def __init__(self):
        pass

    @staticmethod
    def get_help_view():
        help_view = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это меню помощи\n"
            "/menu - Показать каталог товаров\n"
            "/cart - Показать содержимое вашей корзины\n"
            "Просто отправьте название товара, чтобы добавить его в корзину."
        )
        return help_view
