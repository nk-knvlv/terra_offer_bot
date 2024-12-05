from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from controllers.product import ProductController
from controllers.cart import CartController


class MenuView:
    def __init__(self, product_controller: ProductController, cart_controller: CartController, category_controller):
        self.product_controller = product_controller
        self.cart_controller = cart_controller
        self.category_controller = category_controller

    async def show(self, update, context):
        query = update.callback_query
        user = query.from_user
        products = self.product_controller.get_all()
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        if not products:
            await update.callback_query.edit_message_text("Каталог пуст.")
        else:
            parent_categories = self.category_controller.get_categories()
            category_view = self.get_category_view(categories=parent_categories)
            reply_markup = InlineKeyboardMarkup([*category_view])

            await update.callback_query.edit_message_text(f"Меню:\n", reply_markup=reply_markup)

    @staticmethod
    def get_category_view(categories):
        # Создаем инлайн-клавиатуру
        category_view = []
        for category in categories:
            category_button = InlineKeyboardButton(
                text=category.name,
                callback_data=f"button_menu_show_category_{category.id}"  # Присоединяем id блюда к callback_data
            )
            category_view.append([category_button])

        return category_view

    async def show_category(self, update, context, category_id):
        keyboard = []
        query = update.callback_query
        user = query.from_user
        category_inner = self.category_controller.get_category_inner(category_id)
        if child_categories := category_inner['categories']:
            categories_view = self.get_category_view(child_categories)
            button_row_list = []
            counter = 0
            for category in categories_view:
                button_row_list.append(category[0])
                counter += 1
                if counter == 2:
                    keyboard.append(button_row_list)
                    counter = 0
                    button_row_list = []
        if products := category_inner['products']:
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
        parent_category = self.category_controller.get_category(category_id)
        category_name = parent_category.name
        message = f"{category_name}:\n"

        if len(keyboard) == 0:
            message = 'Скоро будут...'
        keyboard.append([cart_button])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
