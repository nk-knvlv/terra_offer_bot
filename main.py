import json
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from models import OrderFieldsLang, OrderStatus
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
    get_all_products,
    get_cart_product,
    add_cart_product,
    get_all_cart_products,
    clear_cart,
    first_fill_in,
    get_product_by_id,
    add_order, get_all_orders, get_user_orders
)
import views
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))


def is_admin(user_id):
    if user_id == ADMIN_CHAT_ID:
        return True
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.chat_id)
    user_id = update.message.chat_id

    if is_admin(user_id):
        message = 'Администрирование.'
        settings_button = InlineKeyboardButton("Настройки", callback_data='button_settings')
        orders_button = InlineKeyboardButton("Заказы", callback_data='button_orders')
        reviews_button = InlineKeyboardButton("Отзывы", callback_data='button_reviews')

        keyboard = [
            [settings_button],
            [orders_button],
            [reviews_button],
        ]

    else:
        message = "Добро пожаловать!"

        restaurant_link = 'https://yandex.ru/maps/org/terra/135054299656/?ll=37.510259%2C55.743335&z=16'
        link_button = InlineKeyboardButton("Наш ресторан", url=restaurant_link)
        menu_button = InlineKeyboardButton("Меню", callback_data='button_menu')
        order_button = InlineKeyboardButton("Мои заказы", callback_data='button_orders')
        contacts_button = InlineKeyboardButton("Контакты", callback_data='button_contacts')
        reviews_button = InlineKeyboardButton("Отзывы", callback_data='button_reviews')

        keyboard = [
            [link_button],
            [menu_button],
            [order_button],
            [contacts_button],
            [reviews_button]
        ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await update.message.reply_text(
        message,
        reply_markup=markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это меню помощи\n"
        "/menu - Показать каталог товаров\n"
        "/cart - Показать содержимое вашей корзины\n"
        "Просто отправьте название товара, чтобы добавить его в корзину."
    )
    await update.message.reply_text(help_text)


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


async def start_confirm_order_conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'confirm_order' in query.data:
        await update.callback_query.edit_message_text(
            text="Добро пожаловать в службу доставки! Для начала введите свой номер телефона:"
        )
        return PHONE


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Начало":
        await start(update, context)  # Повторное выполнение функции start
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


PHONE, ADDRESS, COMMENT = range(3)


def get_confirm_order_conversation():
    # Шаги оформления заказа

    confirm_order_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_confirm_order_conversation_handler, pattern='^conversation.*$')],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_handler)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler)],
        },
        fallbacks=[CallbackQueryHandler(callback_cancel_confirm_order, pattern='^conversation_cancel$')],
    )

    return confirm_order_conversation


async def callback_cancel_confirm_order(update: Update, context: CallbackContext):
    await update.message.reply_text("Заказ отменен. Используйте /start для повторного запуска.")
    return ConversationHandler.END


async def phone_handler(update: Update, context: CallbackContext):
    user_phone = update.message.text
    context.user_data['phone'] = user_phone  # Сохраняем номер телефона
    await update.message.reply_text(f"Ваш номер телефона: {user_phone}. Теперь, введите ваш адрес:")
    return ADDRESS


async def address_handler(update: Update, context: CallbackContext):
    user_address = update.message.text
    context.user_data['address'] = user_address  # Сохраняем адрес
    await update.message.reply_text(f"Ваш адрес: {user_address}. Пожалуйста, введите комментарий к заказу:")
    return COMMENT


async def comment_handler(update: Update, context: CallbackContext):
    session = get_session()
    user_comment = update.message.text
    context.user_data['comment'] = user_comment  # Сохраняем комментарий
    # Здесь вы можете обрабатывать заказ
    user = update.message.from_user
    user_id = update.message.chat_id
    username = user.username
    order_details = {
        'Контакт': context.user_data['phone'],
        'Адрес': context.user_data['address'],
        'Коммент': user_comment,
    }  # Замените на ваши данные о заказе

    user_cart_products = get_all_cart_products(session=session, username=username)
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


def main():
    confirm_order_conversation = get_confirm_order_conversation()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cart", view_cart))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(confirm_order_conversation)
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^button.*$'))
    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    prepare()
main()
