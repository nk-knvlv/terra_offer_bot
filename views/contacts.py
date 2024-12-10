from telegram import InlineKeyboardMarkup

from views.view import View


class ContactsView(View):
    def __init__(self, admin_controller):
        self.admin_controller = admin_controller

    async def show(self, update, context):
        admin_username = await self.admin_controller.get_admin_nickname(update, context)
        keyboard = []
        contacts_view = (
            "Будем рады помочь:\n"
            "Наш рабочий номер +79637707161\n"
            f"Поддержка - {admin_username}"
        )
        footer = self.get_footer(update, context)
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(contacts_view, reply_markup=reply_markup)
