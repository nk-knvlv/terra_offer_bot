from telegram import InlineKeyboardMarkup

from views.view import View


class HelpView(View):

    def __init__(self):
        pass

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
        footer = self.get_footer(update, context)
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(help_view, reply_markup=reply_markup)
