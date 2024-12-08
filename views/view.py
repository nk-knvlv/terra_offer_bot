from telegram import InlineKeyboardButton


class View:
    @staticmethod
    def get_back_button():
        return InlineKeyboardButton(
            text=f'⬅',
            callback_data=f"button_back"
        )

    @staticmethod
    def get_start_button():
        return InlineKeyboardButton(
            text=f'🏠',
            callback_data=f"button_start"
        )

    def get_footer(self, update, context):
        footer = []
        if len(context.user_data['navigation']) > 0:
            back_button = self.get_back_button()
            footer.append(back_button)
        if len(context.user_data['navigation']) > 1:
            start_button = self.get_start_button()
            footer.append(start_button)
        return footer
