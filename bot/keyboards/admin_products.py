from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_products_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Ajouter un produit",
                    callback_data="admin_product_add",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Liste des produits",
                    callback_data="admin_product_list",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Administration",
                    callback_data="admin_home",
                )
            ],
        ]
    )


def admin_product_list_keyboard(products):
    buttons = []

    for product in products:
        status = "🟢" if product.is_active else "🔴"

        buttons.append([
            InlineKeyboardButton(
                text=(
                    f"{status} #{product.id} "
                    f"{product.name} — "
                    f"{product.price:.2f} € "
                    f"(stock {product.stock})"
                ),
                callback_data=f"admin_product:{product.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="➕ Ajouter",
            callback_data="admin_product_add",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Produits",
            callback_data="admin_products",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def admin_product_detail_keyboard(product):
    buttons = []

    buttons.append([
        InlineKeyboardButton(
            text="✏️ Modifier",
            callback_data=f"admin_product_edit:{product.id}",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🗑️ Supprimer",
            callback_data=f"admin_product_delete:{product.id}",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="💰 Modifier le prix",
            callback_data=f"admin_product_price:{product.id}",
        ),
        InlineKeyboardButton(
            text="📊 Modifier le stock",
            callback_data=f"admin_product_stock:{product.id}",
        ),
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🧩 Variantes",
            callback_data=f"admin_variants:{product.id}",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🔄 Changer catégorie",
            callback_data=f"admin_product_move:{product.id}",
        )
    ])

    if product.is_active:
        buttons.append([
            InlineKeyboardButton(
                text="🔴 Désactiver",
                callback_data=f"admin_product_toggle:{product.id}",
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="🟢 Activer",
                callback_data=f"admin_product_toggle:{product.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Liste",
            callback_data="admin_product_list",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Produits",
            callback_data="admin_products",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def product_categories_keyboard(categories) -> InlineKeyboardMarkup:
    buttons = []

    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {category.name}",
                callback_data=f"admin_product_category:{category.id}",
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def admin_variants_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Ajouter une variante",
                    callback_data=f"admin_variant_add:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Liste des variantes",
                    callback_data=f"admin_variant_list:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Retour produit",
                    callback_data=f"admin_product:{product_id}",
                )
            ],
        ]
    )


def admin_variant_list_keyboard(variants, product_id):
    buttons = []

    for variant in variants:
        buttons.append([
            InlineKeyboardButton(
                text=(
                    f"#{variant.id} "
                    f"{variant.name} "
                    f"- {variant.price:.2f}€ "
                    f"(stock {variant.stock})"
                ),
                callback_data=f"admin_variant_delete:{variant.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Variantes",
            callback_data=f"admin_variants:{product_id}",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
