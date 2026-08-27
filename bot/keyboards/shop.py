from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def categories_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = []

    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {category.name}",
                callback_data=f"category:{category.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Menu principal",
            callback_data="back_to_menu",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(products) -> InlineKeyboardMarkup:
    buttons = []

    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"📦 {product.name} — {product.price:.2f} €",
                callback_data=f"product:{product.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Catégories",
            callback_data="menu_shop",
        ),
        InlineKeyboardButton(
            text="🏠 Menu",
            callback_data="back_to_menu",
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧺 Ajouter au panier",
                    callback_data=f"add_cart:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Produits",
                    callback_data=f"category:{category_id}",
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
