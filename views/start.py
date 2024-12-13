from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from views.view import View


class StartView(View):
    def __init__(self, admin_controller, navigation_controller):
        self.admin_controller = admin_controller
        self.navigation_controller = navigation_controller

    async def show(self, update: Update, context):
        context.user_data['navigation'] = ['view-start']
        if 'message_history' not in context.user_data:
            context.user_data['message_history'] = []
        if update.message:
            print(update.message.chat_id)
            user = update.message.from_user
            chat_id = update.message.chat_id
            context.user_data['message_history'].append(update.message.message_id)
            # Если в истории больше одного сообщения, удаляем их
            while len(context.user_data['message_history']) > 1:
                message_id_to_delete = context.user_data['message_history'].pop()  # Убираем старое сообщение
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id_to_delete)
                except Exception as e:
                    print(f"Error while deleting message {message_id_to_delete}: {e}")
        else:
            query = update.callback_query
            user = query.from_user
        if self.admin_controller.is_admin(user.id):
            message = 'Администрирование.'
            settings_button = InlineKeyboardButton("Настройки", callback_data='view-menu')
            orders_button = InlineKeyboardButton("Заказы", callback_data='view-order')

            keyboard = [
                [settings_button],
                [orders_button],
            ]

        else:
            message = "Добро пожаловать!"

            restaurant_link = 'https://yandex.ru/maps/org/terra/135054299656/?ll=37.510259%2C55.743335&z=16'
            link_button = InlineKeyboardButton("Наш ресторан", url=restaurant_link)
            menu_button = InlineKeyboardButton("📜 Меню", callback_data='view-menu')
            order_button = InlineKeyboardButton("🛍️ Мои заказы", callback_data='view-order')
            contacts_button = InlineKeyboardButton("📞 Контакты", callback_data='view-contacts')

            keyboard = [
                [link_button],
                [menu_button],
                [order_button],
                [contacts_button],
            ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if update.message:
            sent_message = await update.message.reply_text(
                message,
                reply_markup=markup
            )
        else:
            sent_message = await update.callback_query.edit_message_text(
                message,
                reply_markup=markup
            )
        context.user_data['message_history'].append(sent_message.message_id)
