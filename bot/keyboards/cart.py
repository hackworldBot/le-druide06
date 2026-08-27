from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def cart_keyboard(items) -> InlineKeyboardMarkup:
    buttons = []

    for item in items:
        buttons.append([
            InlineKeyboardButton(
                text="➖",
                callback_data=f"cart_decrease:{item['id']}",
            ),
            InlineKeyboardButton(
                text=str(item["quantity"]),
                callback_data=f"cart_item:{item['id']}",
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=f"cart_increase:{item['id']}",
            ),
            InlineKeyboardButton(
                text="🗑️",
                callback_data=f"cart_delete:{item['id']}",
            ),
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Passer commande",
            callback_data="checkout",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🛍️ Continuer mes achats",
            callback_data="menu_shop",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Menu principal",
            callback_data="back_to_menu",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def checkout_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirmer la commande",
                    callback_data="confirm_order",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Annuler",
                    callback_data="cart_view",
                )
            ],
        ]
    )
