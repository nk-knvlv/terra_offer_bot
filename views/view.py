from telegram import InlineKeyboardButton


class View:
    @staticmethod
    def get_back_button():
        return InlineKeyboardButton(
            text=f'⬅',
            callback_data=f"back"
        )

    @staticmethod
    def get_start_button():
        return InlineKeyboardButton(
            text=f'🏠',
            callback_data=f"start"
        )

    def get_footer(self, navigation):
        footer = []
        if len(navigation) > 0:
            back_button = self.get_back_button()
            footer.append(back_button)
        if len(navigation) > 1:
            start_button = self.get_start_button()
            footer.append(start_button)
        return footer
