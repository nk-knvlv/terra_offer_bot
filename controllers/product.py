from telegram import InlineKeyboardButton

from models.product import ProductModel


class ProductController:
    def __init__(self, product_model: ProductModel, cart_model):
        self.product_model = product_model
        self.cart_model = cart_model

    def get_all(self):
        return self.product_model.get_all_products()

    def get_products_by_category(self, category):
        return self.product_model.get_products_by_category(category)

    def get_product_buttons(self, product, user):
        product_name_button = InlineKeyboardButton(
            text=f"{product.name}\n{product.price:.0f} ₽",
            callback_data=f"view-product-{product.id}"
            # Присоединяем id блюда к callback_data
        )
        add_button = self.get_add_button(product.id, user_id=user.id)
        decrease_button = self.get_decrease_button(product.id)
        return [product_name_button, decrease_button, add_button]

    def get_product_by_id(self, product_id):
        return self.product_model.get_product_by_id(product_id)

    @staticmethod
    def get_decrease_button(product_id):
        decrease_button_text = '➖'
        decrease_button = InlineKeyboardButton(
            text=decrease_button_text,
            callback_data=f"action-cart_product-decrease-{product_id}"  # Присоединяем id блюда к callback_data
        )
        return decrease_button

    def get_add_button(self, product_id, user_id):
        add_button_text = '➕'
        cart_product = self.cart_model.get_product_by_id(product_id=product_id, user_id=user_id)
        if cart_product and cart_product.quantity:
            add_button_text += f' ({cart_product.quantity})'
        add_button = InlineKeyboardButton(
            text=add_button_text,
            callback_data=f"action-cart_product-add-{product_id}"  # Присоединяем id блюда к callback_data
        )
        return add_button

    @staticmethod
    async def del_photo(update, context):
        if 'last_photo_message_id' in context.user_data:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                 message_id=context.user_data['last_photo_message_id'])
                del context.user_data['last_photo_message_id']  # Удаляем ID после удаления сообщения
            except Exception as e:
                print("Не удалось удалить сообщение:", e)

    def get_products_keyboard(self, user, products):
        product_button_view = []
        for product in products:
            product_buttons = self.get_product_buttons(product=product, user=user)
            product_button_view.append([product_buttons[0], product_buttons[2]])
        return product_button_view
