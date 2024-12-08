from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes
from views.view import View


class StartView(View):
    def __init__(self, admin_controller):
        self.admin_controller = admin_controller

    async def show(self, update: Update, context):
        context.user_data['navigation'] = []
        if update.message:
            print(update.message.chat_id)
            user = update.message.from_user
        else:
            query = update.callback_query
            user = query.from_user
        if self.admin_controller.is_admin(user.id):
            message = 'Администрирование.'
            settings_button = InlineKeyboardButton("Настройки", callback_data='button_settings')
            orders_button = InlineKeyboardButton("Заказы", callback_data='button_orders')

            keyboard = [
                [settings_button],
                [orders_button],
            ]

        else:
            message = "Добро пожаловать!"

            restaurant_link = 'https://yandex.ru/maps/org/terra/135054299656/?ll=37.510259%2C55.743335&z=16'
            link_button = InlineKeyboardButton("Наш ресторан", url=restaurant_link)
            menu_button = InlineKeyboardButton("📜 Меню", callback_data='button_menu')
            order_button = InlineKeyboardButton("🛍️ Мои заказы", callback_data='button_orders')
            contacts_button = InlineKeyboardButton("📞 Контакты", callback_data='button_contacts')

            keyboard = [
                [link_button],
                [menu_button],
                [order_button],
                [contacts_button],
            ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if update.message:
            await update.message.reply_text(
                message,
                reply_markup=markup
            )
        else:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=markup
            )
