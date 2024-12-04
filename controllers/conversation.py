from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from models.order import OrderModel
import json


class ConversationController:
    PHONE, ADDRESS, COMMENT = range(3)

    def __init__(self, order_controller, admin_controller, cart_controller):
        self.order_controller = order_controller
        self.admin_controller = admin_controller
        self.cart_controller = cart_controller

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

    @staticmethod
    async def callback_cancel_confirm_order(update, context):
        await update.message.reply_text("Заказ отменен. Используйте /start для повторного запуска.")
        return ConversationHandler.END

    async def phone_handler(self, update, context):
        user_phone = update.message.text
        context.user_data['phone'] = user_phone  # Сохраняем номер телефона
        await update.message.reply_text(f"Ваш номер телефона: {user_phone}. Теперь, введите ваш адрес:")
        return self.ADDRESS

    async def address_handler(self, update, context):
        user_address = update.message.text
        context.user_data['address'] = user_address  # Сохраняем адрес
        await update.message.reply_text(f"Ваш адрес: {user_address}. Пожалуйста, введите комментарий к заказу:")
        return self.COMMENT

    async def comment_handler(self, update, context):
        user_comment = update.message.text
        context.user_data['comment'] = user_comment  # Сохраняем комментарий
        # Здесь вы можете обрабатывать заказ
        user = update.message.from_user
        user_cart_products = self.cart_controller.get_all_products(user_id=user.id)
        dict_cart_products = {}
        for cart_product in user_cart_products:
            dict_cart_products[cart_product.product.name] = cart_product.quantity

        self.order_controller.add(
            user=user,
            phone=context.user_data['phone'],
            address=context.user_data['address'],
            comment=user_comment,
            json_products=json.dumps(dict_cart_products)
        )

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

        order_details = {
            'username': user,
            'phone': context.user_data['phone'],
            'address': context.user_data['address'],
            'comment': user_comment,
            'json_products': json.dumps(dict_cart_products)
        }

        await self.admin_controller.send_new_order_notice(order_details, context=context)

        return ConversationHandler.END

    async def start_confirm_order_conversation_handler(self, update, context):
        query = update.callback_query
        await query.answer()
        if 'confirm_order' in query.data:
            await update.callback_query.edit_message_text(
                text="Добро пожаловать в службу доставки! Для начала введите свой номер телефона:"
            )
            return self.PHONE
