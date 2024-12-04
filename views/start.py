from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes


class StartView:
    def __init__(self, admin_controller):
        self.admin_controller = admin_controller

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(update.message.chat_id)
        user = update.message.from_user

        if self.admin_controller.is_admin(user.id):
            message = 'Администрирование.'
            settings_button = InlineKeyboardButton("Настройки", callback_data='button_settings')
            orders_button = InlineKeyboardButton("Заказы", callback_data='button_orders')
            reviews_button = InlineKeyboardButton("Отзывы", callback_data='button_reviews')

            keyboard = [
                [settings_button],
                [orders_button],
                [reviews_button],
            ]

        else:
            message = "Добро пожаловать!"

            restaurant_link = 'https://yandex.ru/maps/org/terra/135054299656/?ll=37.510259%2C55.743335&z=16'
            link_button = InlineKeyboardButton("Наш ресторан", url=restaurant_link)
            menu_button = InlineKeyboardButton("Меню", callback_data='button_menu')
            order_button = InlineKeyboardButton("Мои заказы", callback_data='button_orders')
            contacts_button = InlineKeyboardButton("Контакты", callback_data='button_contacts')
            reviews_button = InlineKeyboardButton("Отзывы", callback_data='button_reviews')

            keyboard = [
                [link_button],
                [menu_button],
                [order_button],
                [contacts_button],
                [reviews_button]
            ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await update.message.reply_text(
            message,
            reply_markup=markup
        )
