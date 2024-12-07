from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler
)

from dotenv import load_dotenv

from controllers.cart import CartController
from controllers.category import CategoryController
from controllers.order import OrderController
from controllers.product import ProductController
from db import DB
import os

from models.cart import CartModel
from models.category import CategoryModel
from models.order import OrderModel

from controllers.conversation import ConversationController
from controllers.admin import AdminController
from models.product import ProductModel
from views.cart import CartView
from views.contacts import ContactsView

from views.help import HelpView
from views.menu import MenuView
from views.order import OrderView
from views.start import StartView


class Bot:
    def __init__(self):
        load_dotenv()

        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
        self.views = {}
        self.controllers = {}

    async def button_handler(self, update: Update, context: CallbackContext):
        query_str = update.callback_query.data
        callback = query_str.replace('button_', '')
        user = update.callback_query.from_user
        print(context.user_data['navigation'])
        print(callback)
        await update.callback_query.answer()  # Обязательно отвечаем на запрос

        if callback == 'back':
            context.user_data['navigation'].pop()
            callback = context.user_data['navigation'][1] + context.user_data['navigation'][-1]
        if callback == 'start':
            context.user_data['navigation'] = ['start']
            await self.views['start_view'].show(update, context)
        if 'cart' in callback:
            if 'add' in callback:
                product_id = callback.split('_')[-1]
                await self.controllers['cart_controller'].add_product(product_id=product_id, user=user)
                callback = context.user_data['navigation'][1] + context.user_data['navigation'][-1]
                context.user_data['navigation'].pop()

            else:
                context.user_data['navigation'].append('cart')
                await self.views['cart_view'].show(update, context)

        if callback == 'orders':
            context.user_data['navigation'].append('orders')
            await self.views['order_view'].show(update=update, context=context, user=user)

        if callback == 'contacts':
            context.user_data['navigation'].append('contacts')
            await self.views['contacts_view'].show(update=update, context=context)

        if 'menu' in callback:
            if callback == 'menu':
                context.user_data['navigation'].append('menu')
                await self.views['menu_view'].show(update, context)
            if 'category' in callback:
                category_id = int(callback.split('_')[-1])
                category_str = f'category_{category_id}'
                if context.user_data['navigation'][-1] is not category_str:
                    context.user_data['navigation'].append(category_str)
                await self.views['menu_view'].show_category(update, context, category_id)
            if 'product_info' in callback:
                product_id = int(callback.split('_')[-1])
                context.user_data['navigation'].append(f'product_{product_id}')
                await update.callback_query.edit_message_text(text=f"Тут инфо про продукт {product_id}")

    def main(self):
        db = DB()
        db.prepare()
        bot = Application.builder().token(self.TELEGRAM_TOKEN).build()

        # models
        cart_model = CartModel(db)
        order_model = OrderModel(db)
        product_model = ProductModel(db)
        category_model = CategoryModel(db)

        # controllers
        admin_controller = AdminController(self.ADMIN_CHAT_ID)
        cart_controller = CartController(cart_model=cart_model, product_model=product_model)
        order_controller = OrderController(order_model=order_model, admin_controller=admin_controller)
        conversation_controller = ConversationController(order_controller, admin_controller, cart_controller)
        confirm_order_conversation = conversation_controller.get_confirm_order_conversation()
        product_controller = ProductController(product_model=product_model)
        category_controller = CategoryController(category_model=category_model, product_model=product_model)

        # views
        start_view = StartView(admin_controller=admin_controller)
        help_view = HelpView()
        menu_view = MenuView(product_controller=product_controller, cart_controller=cart_controller,
                             category_controller=category_controller)
        order_view = OrderView(admin_controller=admin_controller, order_controller=order_controller)
        cart_view = CartView(cart_controller)
        contacts_view = ContactsView(admin_controller=admin_controller)
        self.views = {
            'start_view': start_view,
            'help_view': help_view,
            'menu_view': menu_view,
            'order_view': order_view,
            'cart_view': cart_view,
            'contacts_view': contacts_view,
        }
        self.controllers = {
            'admin_controller': admin_controller,
            'cart_controller': cart_controller
        }
        # handlers
        bot.add_handler(confirm_order_conversation)
        bot.add_handler(CommandHandler("start", start_view.show))
        bot.add_handler(CommandHandler("help", help_view.show))
        bot.add_handler(CallbackQueryHandler(self.button_handler, pattern='^button.*$'))

        # Запуск бота
        bot.run_polling()


if __name__ == '__main__':
    terra_bot = Bot()
    terra_bot.main()
