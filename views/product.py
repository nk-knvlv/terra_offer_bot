from telegram import InlineKeyboardMarkup
import os

from views.view import View


class ProductView(View):
    def __init__(self, product_controller, navigation_controller):
        self.product_controller = product_controller
        self.navigation_controller = navigation_controller

    async def show(self, update, context):
        product_id = context.user_data['product_id']
        user = update.callback_query.from_user
        keyboard = []
        product = self.product_controller.get_product_by_id(product_id)
        await update.callback_query.answer()  # Обязательно отвечаем на запрос
        product_buttons = self.product_controller.get_product_buttons(product, user=user)
        keyboard.append([product_buttons[1], product_buttons[2]])
        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = (f"{product.name} - {product.price:.0f} ₽\n\n"
                   f"{product.description}")
        if product.photo_path and os.path.exists(
                product.photo_path) and 'last_photo_message_id' not in context.user_data:
            last_message = await update.callback_query.edit_message_text(
                text="Загрузка..."
            )
            with open(product.photo_path, 'rb') as photo:
                photo_message = await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
                # Сохраняем ID фото сообщения, если потребуется для удаления
                context.user_data['last_photo_message_id'] = photo_message.message_id
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                             message_id=last_message.message_id)
            sent_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message,
                                                          reply_markup=reply_markup)
        else:
            sent_message = await update.callback_query.edit_message_text(message, reply_markup=reply_markup)

        return sent_message
