from sqlalchemy.orm import declarative_base
import json
from telegram import Update
from models.enums import OrderFieldsLang, OrderStatus
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
    CallbackQueryHandler
)
from dotenv import load_dotenv
from db import (
    prepare,
    get_session,
    get_cart_product,
    add_cart_product,
    get_all_cart_products,
    get_product_by_id,
    add_order, get_all_orders, get_user_orders
)
from views.help import HelpView
from db import DB
import os
from controllers.conversation import ConversationController

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))


class Bot:
    def __init__(self):
        pass

    async def main(self):
        db = DB()
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        conversation_controller = ConversationController()


        confirm_order_conversation = conversation_controller.get_confirm_order_conversation()
        app.add_handler(
            CommandHandler("start", lambda update, context: self.view_start(update, context, "Hello", "World")))
        app.add_handler(CommandHandler("start", self.view_start))

        # Добавляем обработчики команд
        app.add_handler(CommandHandler("help", self.view_help))
        # app.add_handler(CommandHandler("cart", view_cart))
        app.add_handler(confirm_order_conversation)
        app.add_handler(CallbackQueryHandler(button_handler, pattern='^button.*$'))

        # Запуск бота
        app.run_polling()

    def is_admin(user_id):
        if user_id == ADMIN_CHAT_ID:
            return True
        return False

    async def view_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    async def view_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_view = HelpView.get_help_view()
        await update.message.reply_text(help_view)

    async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu_view = views.get_menu_view()

    def get_order_view(order, user_id):
        order_date = f"{order.date.month:02}/{order.date.day:02} {order.date.hour:02}:{order.date.minute:02}"
        username = ''
        user_info = ''
        if is_admin(user_id=user_id):
            username = ' - @' + order.username
            excluded_fields = ['id', 'username', 'products', '_sa_instance_state', 'date', 'status']
            user_info = '\n' + "\n".join(
                f"{OrderFieldsLang[field].value.capitalize()}: {value}"
                for field, value in order.__dict__.items()
                if field not in excluded_fields
            )
            user_info += f'\nCтатус: {OrderStatus(order.status).value}'
        info_str = (f'{('Заказ ' + order_date + username)}'
                    f'{user_info}'
                    )
        order_products = json.loads(order.products)
        products_str = '\nКорзина:\n' + "\n".join(
            f"{product_name}: {quantity} шт"
            for product_name, quantity in order_products.items()
        )

        order_view = (f'\n{info_str}\n '
                      f'{products_str}')
        return order_view

    async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE, orders):
        query = update.callback_query
        user_id = query.from_user.id
        # Формируем текст в виде таблицы с использованием HTML
        if orders:
            orders_view = f'{'Заказы'}'

            for order in orders:  # Пропускаем заголовок
                order_view = get_order_view(order, user_id)
                orders_view += '\n\n|==========================|\n' + order_view

        else:
            orders_view = 'Заказов нет'
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(orders_view)

    async def add_to_cart(product_id, username):
        session = get_session()

        product = get_product_by_id(session, product_id)
        if product:
            # user_id = update.message.chat_id
            product_id = product.id
            cart_product = get_cart_product(session, username, product_id)
            if cart_product:
                cart_product.quantity += 1
                session.commit()
            else:
                add_cart_product(session, username, product_id, quantity=1)

    async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu_button = InlineKeyboardButton("Меню", callback_data='button_menu')
        confirm_button = InlineKeyboardButton("Подтвердить заказ", callback_data='conversation_confirm_order')
        keyboard = [
            [
                menu_button,
                confirm_button
            ]
        ]
        query = update.callback_query
        session = get_session()
        user_id = query.from_user.id
        username = query.from_user.username
        cart_products = get_all_cart_products(session=session, username=username)
        if cart_products:
            message = "Ваша корзина:\n"
            total = 0
            for cart_product in cart_products:
                product_total = cart_product.quantity * cart_product.product.price
                message += f"{cart_product.product.name} - {cart_product.quantity} шт. - {product_total:.2f} RUB\n"
                total += product_total
            message += f"\nИтого: {total:.2f} RUB"
        else:
            message = "Ваша корзина пуста."

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)

    # TODO подтверждение
    async def order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("Подтвердить заказ", callback_data='conversation_start_confirm_order')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Вы хотите подтвердить ваш заказ?", reply_markup=reply_markup)


    async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "Начало":
            await view_start(update, context)  # Повторное выполнение функции start
        elif update.message.text == "Меню":
            await menu(update, context)

    async def button_handler(update: Update, context: CallbackContext):
        session = get_session()
        query_str = update.callback_query.data
        callback = query_str.replace('button_', '')
        user_id = update.callback_query.from_user.id
        username = update.callback_query.from_user.username
        print(callback)

        await update.callback_query.answer()  # Обязательно отвечаем на запрос

        if callback == 'menu':
            await menu(update, context)

        if callback == 'cart':
            await view_cart(update, context)

        if callback == 'orders':
            if is_admin(user_id=user_id):
                orders = get_all_orders(session=session)

            else:
                orders = get_user_orders(session=session, username=username)

            await view_orders(update=update, context=context, orders=orders)

        if 'get_product_info' in callback:
            await update.callback_query.edit_message_text(text="Тут инфо про продукт")

        if 'add_to_cart' in callback:
            product_id = callback.split('_')[3]
            await add_to_cart(product_id=product_id, username=username)
            await menu(update, context)


if __name__ == '__main__':
    bot = Bot()
    bot.main()
