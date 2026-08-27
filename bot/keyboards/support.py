from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Problème avec une commande",
                    callback_data="support_order",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛍️ Question sur un produit",
                    callback_data="support_product",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Question sur le paiement",
                    callback_data="support_payment",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Autre demande",
                    callback_data="support_other",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu principal",
                    callback_data="back_to_menu",
                )
            ],
        ]
    )
