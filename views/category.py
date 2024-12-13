from telegram import InlineKeyboardMarkup
from telegram.error import BadRequest

from views.view import View


class CategoryView(View):
    def __init__(self, category_controller, navigation_controller, cart_product_controller, product_controller):
        self.category_controller = category_controller
        self.navigation_controller = navigation_controller
        self.cart_product_controller = cart_product_controller
        self.product_controller = product_controller

    async def show(self, update, context):
        category_id = context.user_data['category_id']
        keyboard = []
        query = update.callback_query
        user = query.from_user
        category_inner = self.category_controller.get_category_inner(category_id)
        if child_categories := category_inner['categories']:
            category_keyboard = self.category_controller.get_category_keyboard(child_categories)
            keyboard += category_keyboard

        if products := category_inner['products']:
            product_buttons_view = self.product_controller.get_products_keyboard(products=products, user=user)
            keyboard += product_buttons_view
        parent_category = self.category_controller.get_category(category_id)
        category_name = parent_category.name
        message = f"{category_name}:\n"
        if len(keyboard) == 0:
            message = 'Скоро будут...'
        footer = self.get_footer(self.navigation_controller.get_navigation(context=context))
        cart_button = self.cart_product_controller.get_cart_button(user.id)
        footer.insert(1, cart_button)
        keyboard.append(footer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        try:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        except BadRequest:
            print('одно и то же')
