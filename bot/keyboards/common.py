from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Menu principal",
                    callback_data="back_to_menu",
                )
            ]
        ]
    )
