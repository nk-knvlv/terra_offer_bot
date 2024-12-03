from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)


class ConversationController:
    PHONE, ADDRESS, COMMENT = range(3)

    def __init__(self, update, context, db):
        self.update = update
        self.context = context
        self.db = db

    def get_confirm_order_conversation(self):
        # Шаги оформления заказа

        confirm_order_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_confirm_order_conversation_handler, pattern='^conversation.*$')],
            states={
                self.PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.phone_handler)],
                self.ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.address_handler)],
                self.COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.comment_handler)],
            },
            fallbacks=[CallbackQueryHandler(self.callback_cancel_confirm_order, pattern='^conversation_cancel$')],
        )

        return confirm_order_conversation

    async def callback_cancel_confirm_order(self):
        await self.update.message.reply_text("Заказ отменен. Используйте /start для повторного запуска.")
        return ConversationHandler.END

    async def phone_handler(self):
        user_phone = self.update.message.text
        self.context.user_data['phone'] = user_phone  # Сохраняем номер телефона
        await self.update.message.reply_text(f"Ваш номер телефона: {user_phone}. Теперь, введите ваш адрес:")
        return self.ADDRESS

    async def address_handler(self):
        user_address = self.update.message.text
        self.context.user_data['address'] = user_address  # Сохраняем адрес
        await self.update.message.reply_text(f"Ваш адрес: {user_address}. Пожалуйста, введите комментарий к заказу:")
        return self.COMMENT

    async def comment_handler(self):
        user_comment = self.update.message.text
        self.context.user_data['comment'] = user_comment  # Сохраняем комментарий
        # Здесь вы можете обрабатывать заказ
        user = self.update.message.from_user
        username = user.username

        user_cart_products = get_all_cart_products(session=self.db.session, username=username)
        dict_cart_products = {}
        for cart_product in user_cart_products:
            dict_cart_products[cart_product.product.name] = cart_product.quantity
        order = add_order(
            session=session,
            username=username,
            phone=context.user_data['phone'],
            address=context.user_data['address'],
            comment=user_comment,
            json_products=json.dumps(dict_cart_products)
        )

        # Создаем строку в формате "Ключ: Значение"
        order_view = get_order_view(order, user_id=ADMIN_CHAT_ID)
        # order_view = "\n".join(f"{key.capitalize()}: {value}" for key, value in order_details.items())

        start_button = InlineKeyboardButton('Главное меню', callback_data='button_start')
        menu_button = InlineKeyboardButton('Меню', callback_data='button_menu')
        user_orders_button = InlineKeyboardButton('Мои заказы', callback_data='button_orders')
        # Отправляем сообщение о проверке заказа
        await update.message.reply_text(
            "Ваш заказ проходит проверку. Вы можете вернуться в меню.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        start_button,
                        menu_button,
                        user_orders_button
                    ]
                ],
            )
        )

        # Отправляем уведомление
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID,
                                       text=f"Новый заказ:\n{order_view}")

        return ConversationHandler.END

    def start_confirm_order_conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if 'confirm_order' in query.data:
            await update.callback_query.edit_message_text(
                text="Добро пожаловать в службу доставки! Для начала введите свой номер телефона:"
            )
            return PHONE
