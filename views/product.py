from telegram import InlineKeyboardMarkup
from time import sleep
import os

from views.view import View


class ProductView(View):
    def __init__(self, product_controller, navigation_controller):
        self.product_controller = product_controller
        self.navigation_controller = navigation_controller

    async def show(self, update, context):
        product_id = context.user_data['product_id']
        last_message = await update.callback_query.edit_message_text(
            text="Загрузка..."
        )
        user = update.callback_query.from_user
        keyboard = []
        product = self.product_controller.get_product_by_id(product_id)
        await update.callback_query.answer()  # Обязательно отвечаем на запрос
        if product.photo_path and os.path.exists(product.photo_path):
            with open(product.photo_path, 'rb') as photo:
                photo_message = await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
                # Сохраняем ID фото сообщения, если потребуется для удаления
                context.user_data['last_photo_message_id'] = photo_message.message_id
        await context.bot.delete_message(chat_id=update.effective_chat.id,
                                         message_id=last_message.message_id)
        product_buttons = self.product_controller.get_product_buttons(product, user=user)
        keyboard.append([product_buttons[1], product_buttons[2]])
        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = (f"{product.name} - {product.price:.0f} ₽\n\n"
                   f"{product.description}")
        sent_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message,
                                                      reply_markup=reply_markup)
        return sent_message
