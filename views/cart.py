from telegram.ext import ContextTypes
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


class CartView:
    def __init__(self, cart_controller):
        self.cart_controller = cart_controller

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu_button = InlineKeyboardButton("Меню", callback_data='button_menu')
        confirm_button = InlineKeyboardButton("Подтвердить заказ", callback_data='conversation_confirm_order')
        keyboard = [
            [
                menu_button,
                confirm_button
            ]
        ]
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username
        cart_products = cartget_all_cart_products(session=session, username=username)
        if cart_products:
            message = "Ваша корзина:\n"
            total = 0
            for cart_product in cart_products:
                product_total = cart_product.quantity * cart_product.product.price
                message += f"{cart_product.product.name} - {cart_product.quantity} шт. - {product_total:.2f} RUB\n"
                total += product_total
            message += f"\nИтого: {total:.2f} RUB"
        else:
            message = "Ваша корзина пуста."

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)


    async def get_all(self):
        return