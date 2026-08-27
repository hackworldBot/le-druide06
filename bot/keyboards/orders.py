from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def orders_keyboard(orders) -> InlineKeyboardMarkup:
    buttons = []

    for order in orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"📦 #{order.id} — {order.total:.2f} €",
                callback_data=f"order:{order.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Menu principal",
            callback_data="back_to_menu",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def order_detail_keyboard(
    status: str | None = None,
) -> InlineKeyboardMarkup:

    buttons = []

    if status not in ("COMPLETED", "CANCELLED"):
        buttons.append([
            InlineKeyboardButton(
                text="📦 Mes commandes",
                callback_data="menu_orders",
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="🕘 Historique",
                callback_data="menu_history",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Menu principal",
            callback_data="back_to_menu",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
