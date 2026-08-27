from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ J'accepte",
                    callback_data="accept_terms",
                ),
                InlineKeyboardButton(
                    text="❌ Refuser",
                    callback_data="refuse_terms",
                ),
            ]
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Boutique",
                    callback_data="menu_shop",
                ),
                InlineKeyboardButton(
                    text="🧺 Mon panier",
                    callback_data="menu_cart",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📦 Mes commandes",
                    callback_data="menu_orders",
                ),
                InlineKeyboardButton(
                    text="🕘 Historique",
                    callback_data="menu_history",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Mon compte",
                    callback_data="menu_account",
                ),
                InlineKeyboardButton(
                    text="💬 Support",
                    callback_data="menu_support",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Informations",
                    callback_data="menu_information",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏷️ Promotions",
                    callback_data="menu_promotions",
                ),
            ],
        ]
    )
