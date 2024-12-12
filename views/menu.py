from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.error import BadRequest

from controllers.product import ProductController
from controllers.cart import CartController
from views.view import View


class MenuView(View):
    def __init__(
            self,
            product_controller: ProductController,
            cart_controller: CartController,
            category_controller,
            navigation_controller
    ):
        self.product_controller = product_controller
        self.cart_controller = cart_controller
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
            category_view = self.get_category_buttons_view(categories=parent_categories)
            footer = self.get_footer(self.navigation_controller.navigation)
            cart_button = self.cart_controller.get_cart_button(user.id)
            footer.insert(1, cart_button)
            category_view.append(footer)
            reply_markup = InlineKeyboardMarkup(category_view)
            await update.callback_query.edit_message_text(f"Меню:\n", reply_markup=reply_markup)

    @staticmethod
    def get_category_buttons_view(categories):
        category_view = []
        button_row_list = []
        counter = 0
        for category in categories:
            category_button = InlineKeyboardButton(
                text=category.name,
                callback_data=f"menu_category_{category.id}"  # Присоединяем id блюда к callback_data
            )
            button_row_list.append(category_button)
            counter += 1
            if counter == 2:
                category_view.append(button_row_list)
                counter = 0
                button_row_list = []
        return category_view

    async def show_category(self, update, context, category_id):
        keyboard = []
        query = update.callback_query
        user = query.from_user
        category_inner = self.category_controller.get_category_inner(category_id)
        if child_categories := category_inner['categories']:
            categories_view = self.get_category_buttons_view(child_categories)
            keyboard += categories_view

        if products := category_inner['products']:
            product_buttons_view = self.get_products_view(products=products, user=user)
            keyboard += product_buttons_view
        parent_category = self.category_controller.get_category(category_id)
        category_name = parent_category.name
        message = f"{category_name}:\n"
        if len(keyboard) == 0:
            message = 'Скоро будут...'
        footer = self.get_footer(self.navigation_controller.navigation)
        cart_button = self.cart_controller.get_cart_button(user.id)
        footer.insert(1, cart_button)
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        try:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        except BadRequest:
            print('одно и то же')

    def get_products_view(self, user, products):
        product_button_view = []
        for product in products:
            product_buttons = self.product_controller.get_product_buttons(product=product, user=user)
            product_button_view.append([product_buttons[0], product_buttons[2]])
        return product_button_view
