from telegram import (
    Update,
    LabeledPrice,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton

)
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
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
    first_fill_in, get_product_by_id
)
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
YOUR_ADMIN_CHAT_ID = os.getenv('YOUR_ADMIN_CHAT_ID')
# Шаги оформления заказа
PHONE, ADDRESS, COMMENT = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.chat_id)
    restaurant_link = 'https://yandex.ru/maps/org/terra/135054299656/?ll=37.510259%2C55.743335&z=16'
    link_button = InlineKeyboardButton("Наш ресторан", url=restaurant_link)
    menu_button = InlineKeyboardButton("Меню", callback_data='menu')
    offer_button = InlineKeyboardButton("Мои заказы", callback_data='offers')
    contacts_button = InlineKeyboardButton("Контакты", callback_data='contacts')
    reviews_button = InlineKeyboardButton("Отзывы", callback_data='reviews')

    keyboard = [
        [link_button],
        [menu_button],
        [offer_button],
        [contacts_button],
        [reviews_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await update.message.reply_text(
        "Добро пожаловать! ",
        reply_markup=markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это меню помощи\n"
        "/menu - Показать каталог товаров\n"
        "/cart - Показать содержимое вашей корзины\n"
        "/checkout - Оформить заказ\n"
        "Просто отправьте название товара, чтобы добавить его в корзину."
    )
    await update.message.reply_text(help_text)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = get_session()
    products = get_all_products(session)
    cart_products = get_all_cart_products(session, user_id=user_id)
    if products:
        # Создаем инлайн-клавиатуру
        keyboard = []
        for product in products:
            product_name_button = InlineKeyboardButton(
                text=product.name,
                callback_data=f"get_product_info_{product.id}"  # Присоединяем id блюда к callback_data
            )
            add_button_text = '➕'
            cart_product = get_cart_product(session, user_id, product.id)

            if cart_product and cart_product.quantity:
                add_button_text += f' ({cart_product.quantity})'
            add_button = InlineKeyboardButton(
                text=add_button_text,
                callback_data=f"add_to_cart_{product.id}"  # Присоединяем id блюда к callback_data
            )
            keyboard.append([product_name_button, add_button])

        cart_button = InlineKeyboardButton(
            text='Корзина',
            callback_data=f"cart"
        )
        keyboard.append([cart_button])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем текст с клавиатурой
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text("Выберите блюдо:", reply_markup=reply_markup)
    else:
        await update.callback_query.answer()  # Подтверждаем нажатие кнопки
        await update.callback_query.edit_message_text("Каталог пуст.")


async def add_to_cart(product_id, user_id):
    session = get_session()

    product = get_product_by_id(session, product_id)
    if product:
        # user_id = update.message.chat_id
        product_id = product.id
        cart_product = get_cart_product(session, user_id, product_id)
        if cart_product:
            cart_product.quantity += 1
            session.commit()
        else:
            add_cart_product(session, user_id, product_id, quantity=1)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_button = InlineKeyboardButton("Меню", callback_data='menu')
    confirm_button = InlineKeyboardButton("Подтвердить заказ", callback_data='confirm_order')
    keyboard = [
        [
            menu_button,
            confirm_button
        ]
    ]
    query = update.callback_query
    session = get_session()
    user_id = query.from_user.id
    cart_products = get_all_cart_products(session, user_id)
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


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user_id = update.message.chat_id
    cart_products = get_all_cart_products(session, user_id)
    if cart_products:
        title = "Оплата заказа"
        description = "Оплата товаров из вашей корзины"
        payload = "Custom-Payload"
        currency = "RUB"
        prices = [LabeledPrice(f"{product.product.name} ({product.quantity} шт.)",
                               int(product.product.price * 100 * product.quantity))
                  for product in cart_products]
        await context.bot.send_invoice(
            chat_id=update.message.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency=currency,
            prices=prices,
            start_parameter="test-payment",
        )
    else:
        await update.message.reply_text("Ваша корзина пуста.")


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session()
    user_id = update.message.chat_id
    clear_cart(session, user_id)
    await update.message.reply_text("Спасибо за покупку! Ваш заказ был успешно оформлен.")


async def order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Подтвердить заказ", callback_data='confirm_order')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вы хотите подтвердить ваш заказ?", reply_markup=reply_markup)


async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Обязательно отвечаем на запрос

    if query.data == 'menu':
        await menu(update, context)

    if query.data == 'cart':
        await view_cart(update, context)

    if query.data == 'confirm_order':
        await update.callback_query.edit_message_text(
            text="Добро пожаловать в службу доставки! Для начала введите свой номер телефона:"
        )
        return PHONE

    if 'get_product_info' in query.data:
        await query.edit_message_text(text="Тут инфо про продукт")

    if 'add_to_cart' in query.data:
        product_id = query.data.split('_')[3]
        user_id = query.from_user.id
        await add_to_cart(product_id=product_id, user_id=user_id)
        await menu(update, context)


# def callback_confirm_order(update: Update, context: CallbackContext):


async def callback_cancel_confirm_order(update: Update, context: CallbackContext):
    await update.message.reply_text("Заказ отменен. Используйте /start для повторного запуска.")
    return ConversationHandler.END


def phone_handler(update: Update, context: CallbackContext):
    user_phone = update.message.contact.phone_number
    context.user_data['phone'] = user_phone  # Сохраняем номер телефона
    update.message.reply_text(f"Ваш номер телефона: {user_phone}. Теперь, введите ваш адрес:")
    return ADDRESS


def address_handler(update: Update, context: CallbackContext):
    user_address = update.message.text
    context.user_data['address'] = user_address  # Сохраняем адрес
    update.message.reply_text(f"Ваш адрес: {user_address}. Пожалуйста, введите комментарий к заказу:")
    return COMMENT


async def comment_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_comment = update.message.text
    context.user_data['comment'] = user_comment  # Сохраняем комментарий
    # Здесь вы можете обрабатывать заказ
    user_id = query.from_user.id
    order_details = "Детали заказа"  # Замените на ваши данные о заказе

    # Отправляем сообщение о проверке заказа
    await update.message.reply_text(
        "Ваш заказ проходит проверку. Вы можете вернуться в меню.",
        reply_markup=ReplyKeyboardMarkup(
            [['Главное меню', 'Меню']],
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )

    # Отправляем уведомление
    await context.bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID,
                                   text=f"Пользователь {user_id} подтвердил заказ:\n{order_details}")

    return ConversationHandler.END


def main():
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            PHONE: [MessageHandler(filters.CONTACT, phone_handler)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_handler)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_handler)],
        },
        fallbacks=[CallbackQueryHandler(callback_cancel_confirm_order, pattern='^cancel_confirm_order$')],
        per_message=False
    )

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cart", view_cart))
    app.add_handler(CommandHandler("checkout", checkout))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_to_cart))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(conv_handler)
    # app.add_handler(CallbackQueryHandler(button_callback))
    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    prepare()
main()
