from telegram import InlineKeyboardMarkup
from telegram.error import TimedOut

from views.view import View


class HelpView(View):

    def __init__(self, navigation_controller):
        self.navigation_controller = navigation_controller

    async def show(self, update, context):
        keyboard = []
        help_view = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это меню помощи\n"
            "/menu - Показать каталог товаров\n"
            "/cart - Показать содержимое вашей корзины\n"
            "Просто отправьте название товара, чтобы добавить его в корзину."
        )
        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await update.message.reply_text(help_view, reply_markup=reply_markup)
        except TimedOut:
            print("Время ожидания соединения истекло.")
            # Обработка специфической ошибки
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            # Общая обработка ошибок
