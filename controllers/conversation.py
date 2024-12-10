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
import re


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

        # Проверяем, соответствует ли номер формату +7XXXXXXXXXX, где X - цифра
        pattern = r'^(?:\+7\d{10}|8\d{10})$'
        if bool(re.match(pattern, user_phone)):
            context.user_data['phone'] = user_phone  # Сохраняем номер телефона
            await update.message.reply_text(
                f"Ваш номер телефона: {user_phone}."
                f" Теперь, введите ваш адрес (дом, подъезд, этаж и квартиру):")
            return self.ADDRESS
        else:
            await update.message.reply_text(
                f"Не действительный номер: {user_phone}. Попробуйте еще раз в формате +7XXXXXXXXXX/89XXXXXXXXXX:")
            return self.PHONE

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
        user_cart_products = self.cart_controller.get_products(user_id=user.id)
        dict_cart_products = {}
        for cart_product in user_cart_products:
            dict_cart_products[cart_product.product.name] = cart_product.quantity

        order = await self.order_controller.add(
            user=user,
            phone=context.user_data['phone'],
            address=context.user_data['address'],
            comment=user_comment,
            json_products=json.dumps(dict_cart_products)
        )

        start_button = InlineKeyboardButton('🏠', callback_data='button_start')
        menu_button = InlineKeyboardButton('📜 Меню', callback_data='button_menu')
        user_orders_button = InlineKeyboardButton('🛍️ Мои заказы', callback_data='button_orders')
        # Отправляем сообщение о проверке заказа
        await update.message.reply_text(
            f"Ваш заказ {order.label} проходит проверку. Ожидайте уведомления о подтверждении.",
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
            'id': order.id,
            'username': user.name,
            'phone': order.phone,
            'address': order.address,
            'comment': order.comment,
            'label': order.label,
            'json_products': json.dumps(dict_cart_products)
        }
        self.cart_controller.clear(user.id)
        await self.admin_controller.send_admin_new_order_notice(order_details, context=context)

        return ConversationHandler.END

    async def start_confirm_order_conversation_handler(self, update, context):
        query = update.callback_query
        if self.cart_controller.get_products(user_id=query.from_user.id):
            await query.answer()
            if 'confirm_order' in query.data:
                await update.callback_query.edit_message_text(
                    text="Укажите ваш номер телефона в формате +7 или 89:"
                )
                return self.PHONE
        else:
            await query.answer()
            pass
