from telegram import InlineKeyboardButton

from models.product import ProductModel


class ProductController:
    def __init__(self, product_model: ProductModel):
        self.product_model = product_model

    def get_all(self):
        return self.product_model.get_all_products()

    def get_products_by_category(self, category):
        return self.product_model.get_products_by_category(category)

    def get_product_buttons(self, product, cart_product):
        product_name_button = InlineKeyboardButton(
            text=f"{product.name}\n{product.price:.0f} ₽",
            callback_data=f"button_product_info_{product.id}"
            # Присоединяем id блюда к callback_data
        )
        increase_button = self.get_increase_button(product.id, cart_product=cart_product)
        decrease_button = self.get_decrease_button(product.id)
        return [product_name_button, decrease_button, increase_button]

    def get_product_by_id(self, product_id):
        return self.product_model.get_product_by_id(product_id)

    @staticmethod
    def get_decrease_button(product_id):
        decrease_button_text = '➖'
        decrease_button = InlineKeyboardButton(
            text=decrease_button_text,
            callback_data=f"button_product_decrease_{product_id}"  # Присоединяем id блюда к callback_data
        )
        return decrease_button

    @staticmethod
    def get_increase_button(product_id, cart_product):
        increase_button_text = '➕'

        if cart_product and cart_product.quantity:
            increase_button_text += f' ({cart_product.quantity})'
        increase_button = InlineKeyboardButton(
            text=increase_button_text,
            callback_data=f"button_product_increase_{product_id}"  # Присоединяем id блюда к callback_data
        )
        return increase_button

    @staticmethod
    async def del_photo(update, context):
        if 'last_photo_message_id' in context.user_data:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                 message_id=context.user_data['last_photo_message_id'])
                del context.user_data['last_photo_message_id']  # Удаляем ID после удаления сообщения
            except Exception as e:
                print("Не удалось удалить сообщение:", e)
