from telegram.ext import ContextTypes
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from views.view import View


class CartView(View):
    def __init__(self, cart_controller, product_controller, navigation_controller):
        self.cart_controller = cart_controller
        self.product_controller = product_controller
        self.navigation_controller = navigation_controller

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu_button = InlineKeyboardButton("📜 Меню", callback_data='menu')
        confirm_button = InlineKeyboardButton("✔️ Подтвердить заказ", callback_data='conversation-confirm-order')
        keyboard = [
        ]

        query = update.callback_query
        user = query.from_user
        cart_products = self.cart_controller.get_products(user_id=user.id)

        if cart_products:
            total = 0
            for cart_product in cart_products:
                product = self.product_controller.get_product_by_id(cart_product.product_id)
                product_buttons = self.product_controller.get_product_buttons(product, user=user)
                product_name_button = product_buttons[0]
                keyboard.append([product_name_button])
                products_quantity_buttons = [product_buttons[1], product_buttons[2]]
                keyboard.append(products_quantity_buttons)
                total += product.price * cart_product.quantity
            message = f"Ваша корзина: {total:.0f} ₽\n"
        else:
            message = "Ваша корзина пуста."
        keyboard.append([
            menu_button,
            confirm_button
        ])
        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
