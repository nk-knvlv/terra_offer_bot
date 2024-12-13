from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler
)

from dotenv import load_dotenv

from controllers.cart_product import CartProductController
from controllers.category import CategoryController
from controllers.navigation import NavigationController
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
from views.category import CategoryView
from views.contacts import ContactsView

from views.help import HelpView
from views.menu import MenuView
from views.order import OrderView
from views.product import ProductView
from views.start import StartView


class Bot:
    def __init__(self):
        load_dotenv()

        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
        self.views = {}
        self.controllers = {}

    async def route_handler(self, update: Update, context: CallbackContext):
        route = update.callback_query.data
        if 'navigation' not in context.user_data:
            context.user_data['navigation'] = []
        print(self.controllers['navigation'].get_navigation(context=context))
        print(f"{route}\n")
        await update.callback_query.answer()  # Обязательно отвечаем на запрос

        if route == 'back':
            await self.controllers['product'].del_photo(update, context)
            context.user_data['navigation'].pop()
            route = self.controllers['navigation'].get_current_location(context=context)

        if 'action' in route:
            controller, action, obj_id = route.split('-')[1:]
            action_method = getattr(self.controllers[controller], action)
            await action_method(update, context, obj_id)
            route = self.controllers['navigation'].get_current_location(context=context)

        if 'view' in route:
            self.controllers['navigation'].add_location(context=context, location=route)
            route_path = route.split('-')
            location = route_path[1]
            if len(route_path) > 2:
                context.user_data[f"{location}_id"] = route_path[2]
            # TODO при показе продукта при нажатии на start должно было удаляться
            await self.controllers['product'].del_photo(update, context)
            await self.views[location].show(update=update, context=context)

    def main(self):
        db = DB()
        # db.prepare() # создает таблицы бд
        db.test() # выводит на печать пути фотографий продуктов
        bot = Application.builder().token(self.TELEGRAM_TOKEN).build()

        # models
        cart_model = CartModel(db)
        order_model = OrderModel(db)
        product_model = ProductModel(db)
        category_model = CategoryModel(db)

        # controllers
        admin_controller = AdminController(self.ADMIN_CHAT_ID)
        navigation_controller = NavigationController()
        cart_product_controller = CartProductController(cart_model=cart_model, product_model=product_model)
        order_controller = OrderController(order_model=order_model, admin_controller=admin_controller)
        conversation_controller = ConversationController(order_controller, admin_controller, cart_product_controller)
        confirm_order_conversation = conversation_controller.get_confirm_order_conversation()
        product_controller = ProductController(product_model=product_model, cart_model=cart_model)
        category_controller = CategoryController(category_model=category_model, product_model=product_model)

        # views
        start_view = StartView(admin_controller=admin_controller, navigation_controller=navigation_controller)
        help_view = HelpView(navigation_controller=navigation_controller)
        menu_view = MenuView(product_controller=product_controller, cart_product_controller=cart_product_controller,
                             category_controller=category_controller, navigation_controller=navigation_controller)
        order_view = OrderView(admin_controller=admin_controller, order_controller=order_controller,
                               navigation_controller=navigation_controller)
        cart_view = CartView(cart_product_controller, product_controller, navigation_controller=navigation_controller)
        contacts_view = ContactsView(admin_controller=admin_controller, navigation_controller=navigation_controller)
        product_view = ProductView(product_controller=product_controller, navigation_controller=navigation_controller)
        category_view = CategoryView(
            category_controller,
            navigation_controller,
            cart_product_controller,
            product_controller)
        self.views = {
            'start': start_view,
            'help': help_view,
            'menu': menu_view,
            'order': order_view,
            'cart': cart_view,
            'contacts': contacts_view,
            'product': product_view,
            'category': category_view
        }
        self.controllers = {
            'admin': admin_controller,
            'cart_product': cart_product_controller,
            'product': product_controller,
            'navigation': navigation_controller,
            'order': order_controller
        }
        # handlers
        bot.add_handler(confirm_order_conversation)
        bot.add_handler(CommandHandler("start", start_view.show))
        bot.add_handler(CommandHandler("help", help_view.show))
        bot.add_handler(CallbackQueryHandler(self.route_handler))

        # Запуск бота
        bot.run_polling()


if __name__ == '__main__':
    terra_bot = Bot()
    terra_bot.main()
