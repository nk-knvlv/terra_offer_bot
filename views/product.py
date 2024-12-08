class ProductView:
    def __init__(self, product_controller):
        self.product_controller = product_controller

    async def show(self, update, context, product_id):
        keyboard = []
        product = self.product_controller.get_product_by_id(product_id)
        product_card = []
        if product.photo_path:
            with open(product.photo_path, 'rb') as photo:
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        await update.callback_query.edit_message_text(text=f" {product_id}б", reply_markup=keyboard)
