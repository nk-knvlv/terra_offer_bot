from telegram import (
    InlineKeyboardMarkup,
)
from controllers.product import ProductController
from controllers.cart_product import CartProductController
from views.view import View


class MenuView(View):
    def __init__(
            self,
            product_controller: ProductController,
            cart_product_controller: CartProductController,
            category_controller,
            navigation_controller
    ):
        self.product_controller = product_controller
        self.cart_product_controller = cart_product_controller
        self.category_controller = category_controller
        self.navigation_controller = navigation_controller

    async def show(self, update, context):
        user = update.callback_query.from_user
        products = self.product_controller.get_all()
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        if not products:
            await update.callback_query.edit_message_text("Каталог пуст.")
        else:
            parent_categories = self.category_controller.get_categories()
            category_keyboard = self.category_controller.get_category_keyboard(categories=parent_categories)
            footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
            cart_button = self.cart_product_controller.get_cart_button(user.id)
            footer.insert(1, cart_button)
            category_keyboard.append(footer)
            reply_markup = InlineKeyboardMarkup(category_keyboard)
            await update.callback_query.edit_message_text(f"Меню:\n", reply_markup=reply_markup)
