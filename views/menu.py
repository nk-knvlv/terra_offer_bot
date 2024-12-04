from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from controllers.product import ProductController
from controllers.cart import CartController


class MenuView:
    def __init__(self, product_controller: ProductController, cart_controller: CartController):
        self.product_controller = product_controller
        self.cart_controller = cart_controller

    async def show(self, update, context):
        query = update.callback_query
        user = query.from_user
        products = self.product_controller.get_all()
        if products:
            # Создаем инлайн-клавиатуру
            keyboard = []
            for product in products:
                product_name_button = InlineKeyboardButton(
                    text=product.name,
                    callback_data=f"button_get_product_info_{product.id}"  # Присоединяем id блюда к callback_data
                )
                add_button_text = '➕'
                cart_product = self.cart_controller.get_cart_product_by_id(user_id=user.id, product_id=product.id)

                if cart_product and cart_product.quantity:
                    add_button_text += f' ({cart_product.quantity})'
                add_button = InlineKeyboardButton(
                    text=add_button_text,
                    callback_data=f"button_add_to_cart_{product.id}"  # Присоединяем id блюда к callback_data
                )
                keyboard.append([product_name_button, add_button])

            cart_button = InlineKeyboardButton(
                text='Корзина',
                callback_data=f"button_cart"
            )
            keyboard.append([cart_button])

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Отправляем текст с клавиатурой
            await update.callback_query.answer()  # Подтверждаем нажатие кнопки
            await update.callback_query.edit_message_text("Выберите блюдо:", reply_markup=reply_markup)
        else:
            await update.callback_query.answer()  # Подтверждаем нажатие кнопки
            await update.callback_query.edit_message_text("Каталог пуст.")
