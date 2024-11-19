from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes
from dotenv import load_dotenv
from db import prepare, get_all_items, get_item_by_name, get_cart_item, add_cart_item, get_all_cart_items, clear_cart, \
    first_fill_in
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в наш магазин! Введите /catalog для просмотра товаров.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды:\\n"
        "/start - Начать работу с ботом\\n"
        "/help - Показать это меню помощи\\n"
        "/catalog - Показать каталог товаров\\n"
        "/cart - Показать содержимое вашей корзины\\n"
        "/checkout - Оформить заказ\\n"
        "Просто отправьте название товара, чтобы добавить его в корзину."
    )
    await update.message.reply_text(help_text)


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_session = prepare()
    items = get_all_items(db_session)
    if items:
        message = "Каталог товаров:\\n"
        for item in items:
            message += f"{item.name} - {item.price:.2f} RUB\\n"
        message += "\\nВведите название товара, чтобы добавить его в корзину."
    else:
        message = "Каталог пуст."
    await update.message.reply_text(message)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_session = prepare()
    item_name = update.message.text.strip()

    item = get_item_by_name(db_session, item_name)
    if item:
        user_id = update.message.chat_id
        item_id = item.id
        cart_item = get_cart_item(db_session, user_id, item_id)
        if cart_item:
            cart_item.quantity += 1
        else:
            add_cart_item(db_session, user_id, item_id, quantity=1)
        await update.message.reply_text(f'Товар {item_name} добавлен в корзину.')
    else:
        await update.message.reply_text("Товар не найден. Пожалуйста, введите корректное название товара.")


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_session = prepare()
    user_id = update.message.chat_id
    cart_items = get_all_cart_items(db_session, user_id)
    if cart_items:
        message = "Ваша корзина:\\n"
        total = 0
        for cart_item in cart_items:
            item_total = cart_item.quantity * cart_item.item.price
            message += f"{cart_item.item.name} - {cart_item.quantity} шт. - {item_total:.2f} RUB\\n"
            total += item_total
        message += f"\\nИтого: {total:.2f} RUB"
        message += "\\nВведите /checkout для оформления заказа."
    else:
        message = "Ваша корзина пуста."
    await update.message.reply_text(message)


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_session = prepare()
    user_id = update.message.chat_id
    cart_items = get_all_cart_items(db_session, user_id)
    if cart_items:
        title = "Оплата заказа"
        description = "Оплата товаров из вашей корзины"
        payload = "Custom-Payload"
        currency = "RUB"
        prices = [LabeledPrice(f"{item.item.name} ({item.quantity} шт.)", int(item.item.price * 100 * item.quantity))
                  for item in cart_items]
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
    db_session = prepare()
    user_id = update.message.chat_id
    clear_cart(db_session, user_id)
    await update.message.reply_text("Спасибо за покупку! Ваш заказ был успешно оформлен.")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("cart", view_cart))
    app.add_handler(CommandHandler("checkout", checkout))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_to_cart))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    db_session = prepare()
    first_fill_in(db_session)
main()
