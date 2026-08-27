from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import (
    Order,
    OrderItem,
    User,
    Product,
    Category,
    SupportTicket,
    SupportMessage,
    Information,
    Promotion,
)

from bot.states.admin import (
    ProductStates,
    CategoryStates,
    InformationStates,
    PromotionStates,
)
from bot.states.support import SupportStates

from bot.keyboards.admin_products import (
    admin_products_keyboard,
    admin_product_list_keyboard,
    admin_product_detail_keyboard,
)

from bot.keyboards.admin import (
    admin_main_keyboard,
    admin_orders_keyboard,
    admin_order_detail_keyboard,
    admin_category_list_keyboard,
    admin_category_detail_keyboard,
)


router = Router()

ADMIN_TELEGRAM_ID = 8727592009


def is_admin(telegram_id: int) -> bool:
    return telegram_id == ADMIN_TELEGRAM_ID


async def get_orders():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .order_by(Order.created_at.desc())
        )

        return result.scalars().all()


def status_label(status: str) -> str:
    labels = {
        "PENDING": "🟡 EN ATTENTE",
        "PREPARING": "🔵 EN PRÉPARATION",
        "READY": "🟢 PRÊTE",
        "COMPLETED": "✅ TERMINÉE",
        "CANCELLED": "🔴 ANNULÉE",
    }

    return labels.get(status, status)


async def show_admin_orders(target):
    orders = await get_orders()

    if not orders:
        text = """
👨‍💼 <b>ADMINISTRATION</b>

📦 Aucune commande.
"""
    else:
        pending = sum(
            1 for order in orders
            if order.status == "PENDING"
        )

        preparing = sum(
            1 for order in orders
            if order.status == "PREPARING"
        )

        ready = sum(
            1 for order in orders
            if order.status == "READY"
        )

        completed = sum(
            1 for order in orders
            if order.status == "COMPLETED"
        )

        cancelled = sum(
            1 for order in orders
            if order.status == "CANCELLED"
        )

        text = f"""
👨‍💼 <b>ADMINISTRATION</b>

📦 Commandes : <b>{len(orders)}</b>

🟡 En attente : <b>{pending}</b>
🔵 En préparation : <b>{preparing}</b>
🟢 Prêtes : <b>{ready}</b>
✅ Terminées : <b>{completed}</b>
🔴 Annulées : <b>{cancelled}</b>

Sélectionne une commande :
"""

    keyboard = admin_orders_keyboard(orders)

    if isinstance(target, Message):
        await target.answer(
            text,
            reply_markup=keyboard,
        )
    else:
        await target.message.edit_text(
            text,
            reply_markup=keyboard,
        )


@router.message(Command("admin"))
async def admin_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Accès administrateur refusé."
        )
        return

    await show_admin_home(message)


async def show_admin_home(target):
    text = """
👨‍💼 <b>ADMINISTRATION</b>

Bienvenue dans le panneau d'administration.

Choisissez une section :
"""

    keyboard = admin_main_keyboard()

    if isinstance(target, Message):
        await target.answer(
            text,
            reply_markup=keyboard,
        )
    else:
        await target.message.edit_text(
            text,
            reply_markup=keyboard,
        )


@router.callback_query(
    lambda callback: callback.data == "admin_home"
)
async def admin_home_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await callback.answer()
    await show_admin_home(callback)


async def show_admin_products(target):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .order_by(Product.name)
        )

        products = result.scalars().all()

    text = """
📦 <b>GESTION DES PRODUITS</b>

Choisissez une action :
"""

    keyboard = admin_products_keyboard()

    if isinstance(target, Message):
        await target.answer(
            text,
            reply_markup=keyboard,
        )
    else:
        await target.message.edit_text(
            text,
            reply_markup=keyboard,
        )


@router.callback_query(
    lambda callback: callback.data == "admin_products"
)
async def admin_products_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await callback.answer()
    await show_admin_products(callback)


@router.callback_query(
    lambda callback: callback.data == "admin_product_add"
)
async def admin_product_add_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.set_state(ProductStates.waiting_name)

    await callback.answer()

    await callback.message.edit_text(
        """
➕ <b>AJOUT D'UN PRODUIT</b>

Entrez le <b>nom</b> du produit :
"""
    )


@router.callback_query(
    lambda callback: callback.data == "admin_product_list"
)
async def admin_product_list_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .order_by(Product.name)
        )

        products = result.scalars().all()

    if not products:
        text = """
📋 <b>LISTE DES PRODUITS</b>

Aucun produit dans la base.
"""
    else:
        text = """
📋 <b>LISTE DES PRODUITS</b>

Sélectionnez un produit :
"""

    await callback.answer()

    await callback.message.edit_text(
        text,
        reply_markup=admin_product_list_keyboard(products),
    )


@router.callback_query(
    lambda callback: callback.data.startswith("admin_product:")
)
async def admin_product_detail_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == product_id
            )
        )

        if product is None:
            await callback.answer(
                "Produit introuvable.",
                show_alert=True,
            )
            return

        category = await session.scalar(
            select(Category).where(
                Category.id == product.category_id
            )
        )

    status = "🟢 ACTIF" if product.is_active else "🔴 INACTIF"

    category_name = (
        category.name
        if category is not None
        else "Inconnue"
    )

    text = f"""
📦 <b>PRODUIT #{product.id}</b>

<b>{product.name}</b>

📝 Description :
{product.description or "Aucune description"}

💰 Prix : <b>{product.price:.2f} €</b>
📊 Stock : <b>{product.stock}</b>
📂 Catégorie : <b>{category_name}</b>
📌 Statut : <b>{status}</b>
"""

    await callback.answer()

    await callback.message.edit_text(
        text,
        reply_markup=admin_product_detail_keyboard(product),
    )


@router.callback_query(
    lambda callback: callback.data == "admin_categories"
)
async def admin_categories_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category)
            .order_by(Category.sort_order, Category.name)
        )
        categories = result.scalars().all()

    if not categories:
        text = """
📂 <b>GESTION DES CATÉGORIES</b>

Aucune catégorie dans la base de données.
"""
    else:
        lines = [
            "📂 <b>GESTION DES CATÉGORIES</b>",
            "",
            "Sélectionnez une catégorie :",
        ]

        text = "\n".join(lines)

    await callback.answer()

    await callback.message.edit_text(
        text,
        reply_markup=admin_category_list_keyboard(categories),
    )


@router.callback_query(
    lambda callback: callback.data == "admin_category_add"
)
async def admin_category_add_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.set_state(CategoryStates.waiting_name)

    await callback.answer()

    await callback.message.edit_text(
        """
➕ <b>AJOUT D'UNE CATÉGORIE</b>

Entrez le <b>nom</b> de la catégorie :

Exemple :
<code>Boissons</code>
"""
    )


@router.message(CategoryStates.waiting_name)
async def category_waiting_name(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    if not value:
        await message.answer(
            "❌ Le nom ne peut pas être vide."
        )
        return

    if len(value) > 255:
        await message.answer(
            "❌ Nom trop long (255 caractères maximum)."
        )
        return

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(Category).where(
                Category.name == value
            )
        )

    if existing is not None:
        await message.answer(
            "❌ Une catégorie portant ce nom existe déjà."
        )
        return

    await state.update_data(name=value)
    await state.set_state(CategoryStates.waiting_description)

    await message.answer(
        """
📝 <b>DESCRIPTION</b>

Entrez la description de la catégorie.

<i>Pour ne pas mettre de description :</i>
<code>-</code>
"""
    )


@router.message(CategoryStates.waiting_description)
async def category_waiting_description(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    if value == "-":
        value = None
    elif len(value) > 1000:
        await message.answer(
            "❌ Description trop longue (1000 caractères maximum)."
        )
        return

    await state.update_data(description=value)
    await state.set_state(CategoryStates.waiting_sort_order)

    await message.answer(
        """
🔢 <b>ORDRE D'AFFICHAGE</b>

Entrez le numéro d'ordre.

Exemple :
<code>1</code>

Vous pouvez utiliser <code>0</code> pour l'ordre par défaut.
"""
    )


@router.message(CategoryStates.waiting_sort_order)
async def category_waiting_sort_order(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()

    try:
        sort_order = int(value)
    except ValueError:
        await message.answer(
            "❌ Ordre invalide. Entrez un nombre entier."
        )
        return

    if sort_order < 0:
        await message.answer(
            "❌ L'ordre ne peut pas être négatif."
        )
        return

    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(Category).where(
                Category.name == data["name"]
            )
        )

        if existing is not None:
            await state.clear()
            await message.answer(
                "❌ Cette catégorie existe déjà."
            )
            return

        category = Category(
            name=data["name"],
            description=data.get("description"),
            sort_order=sort_order,
            is_active=True,
        )

        session.add(category)
        await session.commit()
        await session.refresh(category)

    await state.clear()

    await message.answer(
        f"""
✅ <b>CATÉGORIE CRÉÉE</b>

📂 <b>{category.name}</b>

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : <b>{category.sort_order}</b>

📌 Statut : 🟢 ACTIF

🆔 ID : <b>#{category.id}</b>
""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📂 Voir les catégories",
                        callback_data="admin_categories",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Administration",
                        callback_data="admin_home",
                    )
                ],
            ]
        ),
    )


@router.callback_query(
    lambda callback: callback.data == "admin_orders"
)
async def admin_orders_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await callback.answer()
    await show_admin_orders(callback)


@router.callback_query(
    lambda callback: callback.data.startswith("admin_order:")
)
async def admin_order_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    order_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        order = await session.scalar(
            select(Order).where(
                Order.id == order_id
            )
        )

        if order is None:
            await callback.answer(
                "Commande introuvable.",
                show_alert=True,
            )
            return

        result = await session.execute(
            select(OrderItem)
            .where(OrderItem.order_id == order.id)
            .order_by(OrderItem.id)
        )

        items = result.scalars().all()

    lines = [
        f"👨‍💼 <b>COMMANDE #{order.id}</b>",
        "",
        f"📅 {order.created_at:%d/%m/%Y %H:%M}",
        f"📌 Statut : <b>{status_label(order.status)}</b>",
        f"💰 Total : <b>{order.total:.2f} €</b>",
        f"💵 Paiement : <b>{order.payment_method}</b>",
        "",
        "📦 <b>ARTICLES</b>",
        "",
    ]

    for item in items:
        lines.append(
            f"• {item.product_name} "
            f"x{item.quantity} "
            f"= <b>{item.subtotal:.2f} €</b>"
        )

    await callback.answer()

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_order_detail_keyboard(order),
    )


@router.callback_query(
    lambda callback: callback.data.startswith("admin_status:")
)
async def admin_change_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer(
            "Action invalide.",
            show_alert=True,
        )
        return

    order_id = int(parts[1])
    new_status = parts[2]

    allowed = {
        "PENDING": {
            "PREPARING",
            "CANCELLED",
        },
        "PREPARING": {
            "READY",
            "CANCELLED",
        },
        "READY": {
            "COMPLETED",
        },
    }

    async with AsyncSessionLocal() as session:
        order = await session.scalar(
            select(Order).where(
                Order.id == order_id
            )
        )

        if order is None:
            await callback.answer(
                "Commande introuvable.",
                show_alert=True,
            )
            return

        current_status = order.status

        if new_status not in allowed.get(
            current_status,
            set(),
        ):
            await callback.answer(
                f"Transition impossible : "
                f"{current_status} → {new_status}",
                show_alert=True,
            )
            return

        # ==========================================
        # ANNULATION
        # ==========================================
        # Le stock avait été retiré lors de la
        # validation de la commande.
        #
        # On le remet donc uniquement lors du passage
        # vers CANCELLED.
        # ==========================================

        if new_status == "CANCELLED":

            result = await session.execute(
                select(OrderItem)
                .where(
                    OrderItem.order_id == order.id
                )
            )

            items = result.scalars().all()

            for item in items:

                product = await session.scalar(
                    select(Product)
                    .where(
                        Product.id == item.product_id
                    )
                    .with_for_update()
                )

                if product is not None:
                    product.stock += item.quantity

        order.status = new_status

        await session.commit()

    if new_status == "CANCELLED":
        await callback.answer(
            f"🔴 Commande #{order_id} annulée. "
            f"Stock restauré."
        )
    else:
        await callback.answer(
            f"✅ Commande #{order_id} : "
            f"{status_label(new_status)}"
        )

    await admin_order_detail(callback)


# ============================================================
# AJOUT PRODUIT — FORMULAIRE FSM
# ============================================================

@router.message(ProductStates.waiting_name)
async def product_waiting_name(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    name = message.text.strip()

    if not name:
        await message.answer(
            "❌ Le nom ne peut pas être vide.\n\n"
            "Entrez le nom du produit :"
        )
        return

    if len(name) > 255:
        await message.answer(
            "❌ Le nom est trop long (255 caractères maximum).\n\n"
            "Entrez un autre nom :"
        )
        return

    await state.update_data(name=name)
    await state.set_state(ProductStates.waiting_description)

    await message.answer(
        "📝 <b>DESCRIPTION</b>\n\n"
        "Entrez la description du produit.\n\n"
        "Si vous ne voulez pas de description, envoyez :\n"
        "<code>-</code>"
    )


@router.message(ProductStates.waiting_description)
async def product_waiting_description(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    description = message.text.strip()

    if description == "-":
        description = None

    if description is not None and len(description) > 5000:
        await message.answer(
            "❌ Description trop longue.\n\n"
            "Entrez une description plus courte :"
        )
        return

    await state.update_data(description=description)
    await state.set_state(ProductStates.waiting_price)

    await message.answer(
        "💰 <b>PRIX</b>\n\n"
        "Entrez le prix en euros.\n\n"
        "Exemple : <code>12.50</code>"
    )


@router.message(ProductStates.waiting_price)
async def product_waiting_price(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    from decimal import Decimal, InvalidOperation

    value = message.text.strip().replace(",", ".")

    try:
        price = Decimal(value)
    except InvalidOperation:
        await message.answer(
            "❌ Prix invalide.\n\n"
            "Entrez uniquement un nombre.\n"
            "Exemple : <code>12.50</code>"
        )
        return

    if price < 0:
        await message.answer(
            "❌ Le prix ne peut pas être négatif."
        )
        return

    if price > Decimal("99999999.99"):
        await message.answer(
            "❌ Prix trop élevé."
        )
        return

    await state.update_data(price=str(price))
    await state.set_state(ProductStates.waiting_stock)

    await message.answer(
        "📊 <b>STOCK</b>\n\n"
        "Entrez la quantité disponible.\n\n"
        "Exemple : <code>10</code>"
    )


@router.message(ProductStates.waiting_stock)
async def product_waiting_stock(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = message.text.strip()

    try:
        stock = int(value)
    except ValueError:
        await message.answer(
            "❌ Stock invalide.\n\n"
            "Entrez un nombre entier.\n"
            "Exemple : <code>10</code>"
        )
        return

    if stock < 0:
        await message.answer(
            "❌ Le stock ne peut pas être négatif."
        )
        return

    await state.update_data(stock=stock)
    await state.set_state(ProductStates.waiting_category)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order, Category.name)
        )

        categories = result.scalars().all()

    if not categories:
        await state.clear()

        await message.answer(
            "❌ Impossible de créer le produit.\n\n"
            "Aucune catégorie active n'existe."
        )
        return

    from bot.keyboards.admin_products import product_categories_keyboard

    await message.answer(
        "📂 <b>CATÉGORIE</b>\n\n"
        "Choisissez la catégorie du produit :",
        reply_markup=product_categories_keyboard(categories),
    )


@router.callback_query(
    lambda callback: callback.data.startswith("admin_product_category:")
)
async def product_select_category(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    if await state.get_state() != ProductStates.waiting_category.state:
        await callback.answer(
            "Cette opération n'est plus active.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.is_active == True,
            )
        )

        if category is None:
            await callback.answer(
                "Catégorie introuvable.",
                show_alert=True,
            )
            return

        data = await state.get_data()

        from decimal import Decimal

        product = Product(
            category_id=category.id,
            name=data["name"],
            description=data.get("description"),
            price=Decimal(data["price"]),
            stock=data["stock"],
            is_active=True,
        )

        session.add(product)
        await session.commit()
        await session.refresh(product)

    await state.clear()

    await callback.answer("✅ Produit créé !")

    await callback.message.edit_text(
        f"""
✅ <b>PRODUIT CRÉÉ</b>

📦 <b>{product.name}</b>

📝 Description :
{product.description or "Aucune description"}

💰 Prix : <b>{product.price:.2f} €</b>
📊 Stock : <b>{product.stock}</b>
📂 Catégorie : <b>{category.name}</b>
📌 Statut : 🟢 ACTIF

🆔 ID : <b>#{product.id}</b>
"""
    )


# ============================================================
# MODIFICATION PRODUIT
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_product_edit:")
)
async def admin_product_edit_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(Product.id == product_id)
        )

    if product is None:
        await callback.answer(
            "Produit introuvable.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(product_id=product.id)
    await state.set_state(ProductStates.editing_name)

    await callback.answer()

    await callback.message.edit_text(
        f"""
✏️ <b>MODIFICATION DU PRODUIT #{product.id}</b>

Nom actuel :
<b>{product.name}</b>

Entrez le nouveau nom :

<i>Pour conserver le nom actuel, envoyez :</i>
<code>-</code>
"""
    )


@router.message(ProductStates.editing_name)
async def product_editing_name(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = message.text.strip()
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == data["product_id"]
            )
        )

        if product is None:
            await state.clear()
            await message.answer("❌ Produit introuvable.")
            return

        if value != "-":
            if not value:
                await message.answer(
                    "❌ Le nom ne peut pas être vide."
                )
                return

            if len(value) > 255:
                await message.answer(
                    "❌ Nom trop long (255 caractères maximum)."
                )
                return

            product.name = value

        await session.commit()

    await state.set_state(ProductStates.editing_description)

    await message.answer(
        f"""
📝 <b>DESCRIPTION</b>

Description actuelle :
{product.description or "Aucune description"}

Entrez la nouvelle description.

<i>Pour conserver la description actuelle :</i>
<code>-</code>

<i>Pour supprimer la description :</i>
<code>vide</code>
"""
    )


@router.message(ProductStates.editing_description)
async def product_editing_description(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = message.text.strip()
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == data["product_id"]
            )
        )

        if product is None:
            await state.clear()
            await message.answer("❌ Produit introuvable.")
            return

        if value == "-":
            pass
        elif value.lower() == "vide":
            product.description = None
        else:
            if len(value) > 5000:
                await message.answer(
                    "❌ Description trop longue."
                )
                return

            product.description = value

        await session.commit()

    await state.set_state(ProductStates.editing_price)

    await message.answer(
        f"""
💰 <b>PRIX</b>

Prix actuel :
<b>{product.price:.2f} €</b>

Entrez le nouveau prix.

<i>Pour conserver le prix actuel :</i>
<code>-</code>

Exemple :
<code>12.50</code>
"""
    )


@router.message(ProductStates.editing_price)
async def product_editing_price(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    from decimal import Decimal, InvalidOperation

    value = message.text.strip()
    data = await state.get_data()

    if value != "-":
        value = value.replace(",", ".")

        try:
            price = Decimal(value)
        except InvalidOperation:
            await message.answer(
                "❌ Prix invalide.\n\n"
                "Exemple : <code>12.50</code>"
            )
            return

        if price < 0:
            await message.answer(
                "❌ Le prix ne peut pas être négatif."
            )
            return

        if price > Decimal("99999999.99"):
            await message.answer(
                "❌ Prix trop élevé."
            )
            return
    else:
        price = None

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == data["product_id"]
            )
        )

        if product is None:
            await state.clear()
            await message.answer("❌ Produit introuvable.")
            return

        if price is not None:
            product.price = price

        await session.commit()

    await state.set_state(ProductStates.editing_stock)

    await message.answer(
        f"""
📊 <b>STOCK</b>

Stock actuel :
<b>{product.stock}</b>

Entrez le nouveau stock.

<i>Pour conserver le stock actuel :</i>
<code>-</code>

Exemple :
<code>20</code>
"""
    )


@router.message(ProductStates.editing_stock)
async def product_editing_stock(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = message.text.strip()
    data = await state.get_data()

    if value != "-":
        try:
            stock = int(value)
        except ValueError:
            await message.answer(
                "❌ Stock invalide.\n\n"
                "Entrez un nombre entier."
            )
            return

        if stock < 0:
            await message.answer(
                "❌ Le stock ne peut pas être négatif."
            )
            return
    else:
        stock = None

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == data["product_id"]
            )
        )

        if product is None:
            await state.clear()
            await message.answer("❌ Produit introuvable.")
            return

        if stock is not None:
            product.stock = stock

        await session.commit()
        await session.refresh(product)

        category = await session.scalar(
            select(Category).where(
                Category.id == product.category_id
            )
        )

    await state.clear()

    category_name = (
        category.name
        if category is not None
        else "Inconnue"
    )

    await message.answer(
        f"""
✅ <b>PRODUIT MODIFIÉ</b>

📦 <b>{product.name}</b>

📝 Description :
{product.description or "Aucune description"}

💰 Prix : <b>{product.price:.2f} €</b>
📊 Stock : <b>{product.stock}</b>
📂 Catégorie : <b>{category_name}</b>
📌 Statut :
{"🟢 ACTIF" if product.is_active else "🔴 INACTIF"}

🆔 ID : <b>#{product.id}</b>
""",
        reply_markup=admin_product_detail_keyboard(product),
    )


# ============================================================
# MODIFICATION RAPIDE DU PRIX
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_product_price:")
)
async def admin_product_price_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(Product.id == product_id)
        )

    if product is None:
        await callback.answer(
            "Produit introuvable.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(product_id=product.id)
    await state.set_state(ProductStates.editing_price)

    await callback.answer()

    await callback.message.edit_text(
        f"""
💰 <b>MODIFIER LE PRIX</b>

Produit :
<b>{product.name}</b>

Prix actuel :
<b>{product.price:.2f} €</b>

Entrez le nouveau prix :

Exemple :
<code>19.90</code>

<i>Pour conserver le prix actuel :</i>
<code>-</code>
"""
    )


# ============================================================
# MODIFICATION RAPIDE DU STOCK
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_product_stock:")
)
async def admin_product_stock_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(Product.id == product_id)
        )

    if product is None:
        await callback.answer(
            "Produit introuvable.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(product_id=product.id)
    await state.set_state(ProductStates.editing_stock)

    await callback.answer()

    await callback.message.edit_text(
        f"""
📊 <b>MODIFIER LE STOCK</b>

Produit :
<b>{product.name}</b>

Stock actuel :
<b>{product.stock}</b>

Entrez le nouveau stock :

Exemple :
<code>50</code>

<i>Pour conserver le stock actuel :</i>
<code>-</code>
"""
    )


# ============================================================
# ACTIVER / DESACTIVER UN PRODUIT
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_product_toggle:")
)
async def admin_product_toggle_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(Product.id == product_id)
        )

        if product is None:
            await callback.answer(
                "Produit introuvable.",
                show_alert=True,
            )
            return

        product.is_active = not product.is_active

        await session.commit()
        await session.refresh(product)

        category = await session.scalar(
            select(Category).where(
                Category.id == product.category_id
            )
        )

    status = "🟢 ACTIF" if product.is_active else "🔴 INACTIF"

    await callback.answer(
        "✅ Produit activé." if product.is_active
        else "🔴 Produit désactivé."
    )

    await callback.message.edit_text(
        f"""
📦 <b>PRODUIT #{product.id}</b>

<b>{product.name}</b>

📝 Description :
{product.description or "Aucune description"}

💰 Prix : <b>{product.price:.2f} €</b>
📊 Stock : <b>{product.stock}</b>
📂 Catégorie : <b>{category.name if category else "Inconnue"}</b>
📌 Statut : <b>{status}</b>
""",
        reply_markup=admin_product_detail_keyboard(product),
    )


# ============================================================
# DETAIL CATEGORIE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_category:")
)
async def admin_category_detail_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id
            )
        )

    if category is None:
        await callback.answer(
            "Catégorie introuvable.",
            show_alert=True,
        )
        return

    status = "🟢 ACTIF" if category.is_active else "🔴 INACTIF"

    await callback.answer()

    await callback.message.edit_text(
        f"""
📂 <b>CATÉGORIE #{category.id}</b>

<b>{category.name}</b>

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : <b>{category.sort_order}</b>
📌 Statut : <b>{status}</b>
""",
        reply_markup=admin_category_detail_keyboard(category),
    )


# ============================================================
# ACTIVER / DESACTIVER CATEGORIE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_category_toggle:")
)
async def admin_category_toggle_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id
            )
        )

        if category is None:
            await callback.answer(
                "Catégorie introuvable.",
                show_alert=True,
            )
            return

        category.is_active = not category.is_active
        await session.commit()
        await session.refresh(category)

    status = "activée" if category.is_active else "désactivée"

    await callback.answer(
        f"✅ Catégorie {status}."
    )

    status_label = (
        "🟢 ACTIF"
        if category.is_active
        else "🔴 INACTIF"
    )

    await callback.message.edit_text(
        f"""
📂 <b>CATÉGORIE #{category.id}</b>

<b>{category.name}</b>

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : <b>{category.sort_order}</b>
📌 Statut : <b>{status_label}</b>
""",
        reply_markup=admin_category_detail_keyboard(category),
    )


# ============================================================
# MODIFICATION CATEGORIE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_category_edit:")
)
async def admin_category_edit_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id
            )
        )

    if category is None:
        await callback.answer(
            "Catégorie introuvable.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.update_data(category_id=category.id)
    await state.set_state(CategoryStates.editing_name)

    await callback.answer()

    await callback.message.edit_text(
        f"""
✏️ <b>MODIFICATION CATÉGORIE #{category.id}</b>

Nom actuel :
<b>{category.name}</b>

Entrez le nouveau nom.

<i>Pour conserver le nom actuel :</i>
<code>-</code>
"""
    )


@router.message(CategoryStates.editing_name)
async def category_editing_name(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == data["category_id"]
            )
        )

        if category is None:
            await state.clear()
            await message.answer("❌ Catégorie introuvable.")
            return

        if value != "-":
            if not value:
                await message.answer(
                    "❌ Le nom ne peut pas être vide."
                )
                return

            if len(value) > 255:
                await message.answer(
                    "❌ Nom trop long (255 caractères maximum)."
                )
                return

            existing = await session.scalar(
                select(Category).where(
                    Category.name == value,
                    Category.id != category.id,
                )
            )

            if existing is not None:
                await message.answer(
                    "❌ Une catégorie portant ce nom existe déjà."
                )
                return

            category.name = value

        await session.commit()

    await state.set_state(CategoryStates.editing_description)

    await message.answer(
        f"""
📝 <b>DESCRIPTION</b>

Description actuelle :
{category.description or "Aucune description"}

Entrez la nouvelle description.

<i>Pour conserver la description actuelle :</i>
<code>-</code>

<i>Pour supprimer la description :</i>
<code>vide</code>
"""
    )


@router.message(CategoryStates.editing_description)
async def category_editing_description(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == data["category_id"]
            )
        )

        if category is None:
            await state.clear()
            await message.answer("❌ Catégorie introuvable.")
            return

        if value == "-":
            pass
        elif value.lower() == "vide":
            category.description = None
        else:
            if len(value) > 1000:
                await message.answer(
                    "❌ Description trop longue (1000 caractères maximum)."
                )
                return

            category.description = value

        await session.commit()

    await state.set_state(CategoryStates.editing_sort_order)

    await message.answer(
        f"""
🔢 <b>ORDRE D'AFFICHAGE</b>

Ordre actuel :
<b>{category.sort_order}</b>

Entrez le nouvel ordre.

<i>Pour conserver l'ordre actuel :</i>
<code>-</code>
"""
    )


@router.message(CategoryStates.editing_sort_order)
async def category_editing_sort_order(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    value = (message.text or "").strip()
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == data["category_id"]
            )
        )

        if category is None:
            await state.clear()
            await message.answer("❌ Catégorie introuvable.")
            return

        if value != "-":
            try:
                sort_order = int(value)
            except ValueError:
                await message.answer(
                    "❌ Ordre invalide. Entrez un nombre entier."
                )
                return

            if sort_order < 0:
                await message.answer(
                    "❌ L'ordre ne peut pas être négatif."
                )
                return

            category.sort_order = sort_order

        await session.commit()
        await session.refresh(category)

    await state.clear()

    status = (
        "🟢 ACTIF"
        if category.is_active
        else "🔴 INACTIF"
    )

    await message.answer(
        f"""
✅ <b>CATÉGORIE MODIFIÉE</b>

📂 <b>{category.name}</b>

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : <b>{category.sort_order}</b>
📌 Statut : <b>{status}</b>

🆔 ID : <b>#{category.id}</b>
""",
        reply_markup=admin_category_detail_keyboard(category),
    )


# ============================================================
# SUPPRESSION SECURISEE D'UNE CATEGORIE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith("admin_category_delete:")
)
async def admin_category_delete_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id
            )
        )

        if category is None:
            await callback.answer(
                "Catégorie introuvable.",
                show_alert=True,
            )
            return

        result = await session.execute(
            select(Product).where(
                Product.category_id == category.id
            )
        )

        products = result.scalars().all()

    if products:
        await callback.answer(
            f"❌ Suppression impossible : {len(products)} "
            f"produit(s) utilisent cette catégorie.",
            show_alert=True,
        )

        await callback.message.edit_text(
            f"""
⚠️ <b>SUPPRESSION IMPOSSIBLE</b>

📂 Catégorie :
<b>{category.name}</b>

Cette catégorie contient actuellement
<b>{len(products)}</b> produit(s).

Pour protéger tes produits, la catégorie
ne peut pas être supprimée tant qu'elle
est utilisée.

💡 Désactive plutôt la catégorie si tu
ne souhaites plus l'afficher.
""",
            reply_markup=admin_category_detail_keyboard(category),
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        f"""
⚠️ <b>CONFIRMATION DE SUPPRESSION</b>

Voulez-vous vraiment supprimer :

📂 <b>{category.name}</b>

Cette action est définitive.
""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Annuler",
                        callback_data=f"admin_category:{category.id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🗑️ OUI, SUPPRIMER",
                        callback_data=f"admin_category_delete_confirm:{category.id}",
                    )
                ],
            ]
        ),
    )


@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_category_delete_confirm:"
    )
)
async def admin_category_delete_confirm_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.scalar(
            select(Category).where(
                Category.id == category_id
            )
        )

        if category is None:
            await callback.answer(
                "Catégorie introuvable.",
                show_alert=True,
            )
            return

        product = await session.scalar(
            select(Product).where(
                Product.category_id == category.id
            )
        )

        if product is not None:
            await callback.answer(
                "❌ Suppression annulée : la catégorie contient des produits.",
                show_alert=True,
            )
            return

        category_name = category.name

        await session.delete(category)
        await session.commit()

    await callback.answer(
        "✅ Catégorie supprimée."
    )

    await callback.message.edit_text(
        f"""
✅ <b>CATÉGORIE SUPPRIMÉE</b>

La catégorie
<b>{category_name}</b>
a été supprimée avec succès.
""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📂 Voir les catégories",
                        callback_data="admin_categories",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Administration",
                        callback_data="admin_home",
                    )
                ],
            ]
        ),
    )


# ============================================================
# SUPPORT ADMIN
# ============================================================

def admin_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟠 Tickets ouverts",
                    callback_data="admin_support:OPEN",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔵 Tickets en cours",
                    callback_data="admin_support:IN_PROGRESS",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Tous les tickets",
                    callback_data="admin_support:ALL",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Actualiser",
                    callback_data="admin_support:OPEN",
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


def admin_support_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Répondre",
                    callback_data=f"admin_support_reply:{ticket_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔵 Prendre en charge",
                    callback_data=f"admin_support_status:{ticket_id}:IN_PROGRESS",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Fermer le ticket",
                    callback_data=f"admin_support_status:{ticket_id}:CLOSED",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Tickets support",
                    callback_data="admin_support:OPEN",
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


async def show_admin_support(
    callback: CallbackQuery,
    status_filter: str = "OPEN",
):
    async with AsyncSessionLocal() as session:
        query = select(SupportTicket).order_by(
            SupportTicket.updated_at.desc()
        )

        if status_filter != "ALL":
            query = query.where(
                SupportTicket.status == status_filter
            )

        result = await session.execute(query)
        tickets = result.scalars().all()

    if status_filter == "OPEN":
        title = "🟠 <b>TICKETS OUVERTS</b>"
    elif status_filter == "IN_PROGRESS":
        title = "🔵 <b>TICKETS EN COURS</b>"
    else:
        title = "📋 <b>TOUS LES TICKETS</b>"

    if not tickets:
        text = f"""
💬 <b>SUPPORT</b>

{title}

Aucun ticket dans cette catégorie.
"""
    else:
        lines = [
            "💬 <b>SUPPORT</b>",
            "",
            title,
            "",
        ]

        for ticket in tickets:
            if ticket.status == "OPEN":
                icon = "🟠"
            elif ticket.status == "IN_PROGRESS":
                icon = "🔵"
            elif ticket.status == "CLOSED":
                icon = "✅"
            else:
                icon = "📌"

            lines.append(
                f"{icon} <b>#{ticket.id}</b> — "
                f"{ticket.topic}"
            )

        text = "\n".join(lines)

    buttons = []

    for ticket in tickets:
        if ticket.status == "OPEN":
            icon = "🟠"
        elif ticket.status == "IN_PROGRESS":
            icon = "🔵"
        elif ticket.status == "CLOSED":
            icon = "✅"
        else:
            icon = "📌"

        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} #{ticket.id} — {ticket.topic[:35]}",
                callback_data=f"admin_support_ticket:{ticket.id}",
            )
        ])

    buttons.extend(
        admin_support_keyboard().inline_keyboard
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
    )


@router.callback_query(
    lambda callback: callback.data == "admin_support"
)
async def admin_support_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    await callback.answer()
    await show_admin_support(callback, "OPEN")


@router.callback_query(
    lambda callback: (
        callback.data.startswith("admin_support:")
        and callback.data != "admin_support"
    )
)
async def admin_support_filter_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    status_filter = callback.data.split(":", 1)[1]

    if status_filter not in {
        "OPEN",
        "IN_PROGRESS",
        "ALL",
    }:
        await callback.answer(
            "❌ Filtre invalide.",
            show_alert=True,
        )
        return

    await callback.answer()
    await show_admin_support(
        callback,
        status_filter,
    )


@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_support_ticket:"
    )
)
async def admin_support_ticket_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    ticket_id = int(
        callback.data.split(":")[1]
    )

    async with AsyncSessionLocal() as session:
        ticket = await session.scalar(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id
            )
        )

        if ticket is None:
            await callback.answer(
                "❌ Ticket introuvable.",
                show_alert=True,
            )
            return

        result = await session.execute(
            select(SupportMessage)
            .where(
                SupportMessage.ticket_id == ticket.id
            )
            .order_by(SupportMessage.created_at.asc())
        )

        messages = result.scalars().all()

    if ticket.status == "OPEN":
        status = "🟠 OUVERT"
    elif ticket.status == "IN_PROGRESS":
        status = "🔵 EN COURS"
    elif ticket.status == "CLOSED":
        status = "✅ FERMÉ"
    else:
        status = ticket.status

    lines = [
        "💬 <b>TICKET SUPPORT</b>",
        "",
        f"🆔 Ticket : <b>#{ticket.id}</b>",
        f"📌 Sujet : <b>{ticket.topic}</b>",
        f"📊 Statut : <b>{status}</b>",
        f"👤 User ID : <code>{ticket.user_id}</code>",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "",
    ]

    if not messages:
        lines.append("Aucun message.")
    else:
        for item in messages:
            if item.sender_type == "USER":
                sender = "👤 CLIENT"
            else:
                sender = "👨‍💼 ADMIN"

            lines.append(
                f"<b>{sender}</b>"
            )
            lines.append(item.message)
            lines.append("")

    await callback.answer()

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_support_ticket_keyboard(
            ticket.id
        ),
    )


# ============================================================
# SUPPORT ADMIN — PRENDRE EN CHARGE / FERMER
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_support_status:"
    )
)
async def admin_support_status_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer(
            "❌ Action invalide.",
            show_alert=True,
        )
        return

    try:
        ticket_id = int(parts[1])
    except ValueError:
        await callback.answer(
            "❌ Ticket invalide.",
            show_alert=True,
        )
        return

    new_status = parts[2]

    if new_status not in {"IN_PROGRESS", "CLOSED"}:
        await callback.answer(
            "❌ Statut invalide.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        ticket = await session.scalar(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id
            )
        )

        if ticket is None:
            await callback.answer(
                "❌ Ticket introuvable.",
                show_alert=True,
            )
            return

        ticket.status = new_status

        await session.commit()
        await session.refresh(ticket)

    if new_status == "IN_PROGRESS":
        await callback.answer(
            "🔵 Ticket pris en charge."
        )
    else:
        await callback.answer(
            "✅ Ticket fermé."
        )

    # Réafficher le ticket avec son nouvel état
    await admin_support_ticket_callback(callback)


# ============================================================
# SUPPORT ADMIN — DEMANDER UNE RÉPONSE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_support_reply:"
    )
)
async def admin_support_reply_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    try:
        ticket_id = int(
            callback.data.split(":")[1]
        )
    except (ValueError, IndexError):
        await callback.answer(
            "❌ Ticket invalide.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        ticket = await session.scalar(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id
            )
        )

    if ticket is None:
        await callback.answer(
            "❌ Ticket introuvable.",
            show_alert=True,
        )
        return

    if ticket.status == "CLOSED":
        await callback.answer(
            "❌ Ce ticket est fermé.",
            show_alert=True,
        )
        return

    await state.clear()

    await state.update_data(
        support_ticket_id=ticket.id,
    )

    await state.set_state(
        SupportStates.admin_waiting_reply
    )

    await callback.answer()

    await callback.message.edit_text(
        f"""
💬 <b>RÉPONSE AU TICKET #{ticket.id}</b>

📌 Sujet :
<b>{ticket.topic}</b>

✍️ Écrivez maintenant la réponse
à envoyer au client.

<i>Votre prochain message sera envoyé
directement au client.</i>

❌ Pour annuler :
/cancel
"""
    )


# ============================================================
# SUPPORT ADMIN — ENVOYER LA RÉPONSE AU CLIENT
# ============================================================

@router.message(SupportStates.admin_waiting_reply)
async def admin_support_reply_message_handler(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    if not message.text:
        await message.answer(
            "❌ La réponse doit être un message texte."
        )
        return

    if message.text.strip() == "/cancel":
        await state.clear()

        await message.answer(
            "❌ Réponse annulée.",
            reply_markup=admin_main_keyboard(),
        )
        return

    data = await state.get_data()

    ticket_id = data.get("support_ticket_id")

    if not ticket_id:
        await state.clear()

        await message.answer(
            "❌ Ticket introuvable. Veuillez recommencer."
        )
        return

    reply_text = message.text.strip()

    async with AsyncSessionLocal() as session:
        ticket = await session.scalar(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id
            )
        )

        if ticket is None:
            await state.clear()

            await message.answer(
                "❌ Ticket introuvable."
            )
            return

        if ticket.status == "CLOSED":
            await state.clear()

            await message.answer(
                "❌ Ce ticket est déjà fermé."
            )
            return

        # Récupération de l'utilisateur
        user = await session.scalar(
            select(User).where(
                User.id == ticket.user_id
            )
        )

        if user is None:
            await state.clear()

            await message.answer(
                "❌ Utilisateur du ticket introuvable."
            )
            return

        client_telegram_id = user.telegram_id

        # Enregistrement de la réponse admin
        support_message = SupportMessage(
            ticket_id=ticket.id,
            sender_type="ADMIN",
            sender_telegram_id=message.from_user.id,
            message=reply_text,
        )

        session.add(support_message)

        # Une réponse implique que le ticket est en cours
        if ticket.status == "OPEN":
            ticket.status = "IN_PROGRESS"

        await session.commit()

    # Envoi Telegram au client
    try:
        await message.bot.send_message(
            chat_id=client_telegram_id,
            text=f"""
💬 <b>RÉPONSE DU SUPPORT</b>

🆔 Ticket : <b>#{ticket_id}</b>

📌 Sujet :
<b>{ticket.topic}</b>

━━━━━━━━━━━━━━━━━━

{reply_text}

━━━━━━━━━━━━━━━━━━

🙏 Merci pour votre patience.
""",
        )
    except Exception as error:
        await message.answer(
            f"""
⚠️ <b>RÉPONSE ENREGISTRÉE MAIS NON ENVOYÉE</b>

Le message a bien été enregistré dans le ticket #{ticket_id},
mais Telegram n'a pas permis de contacter le client.

Erreur :
<code>{str(error)[:500]}</code>
"""
        )

        await state.clear()
        return

    await state.clear()

    await message.answer(
        f"""
✅ <b>RÉPONSE ENVOYÉE</b>

Votre réponse a été envoyée au client.

🆔 Ticket :
<b>#{ticket_id}</b>

📊 Statut :
<b>🔵 EN COURS</b>
""",
        reply_markup=admin_main_keyboard(),
    )


# ============================================================
# SUPPORT ADMIN — ANNULER LA RÉPONSE
# ============================================================

@router.message(Command("cancel"))
async def admin_support_cancel_command(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    current_state = await state.get_state()

    if current_state != SupportStates.admin_waiting_reply.state:
        return

    await state.clear()

    await message.answer(
        "❌ Réponse annulée.",
        reply_markup=admin_main_keyboard(),
    )


# ============================================================

# ============================================================
# INFORMATIONS ADMIN
# ============================================================

INFORMATION_FIELDS = {
    "presentation": {
        "label": "📝 Présentation",
        "column": "presentation",
        "max_length": 4000,
    },
    "address": {
        "label": "📍 Adresse",
        "column": "address",
        "max_length": 1000,
    },
    "opening_hours": {
        "label": "🕐 Horaires",
        "column": "opening_hours",
        "max_length": 2000,
    },
    "payment": {
        "label": "💶 Paiement",
        "column": "payment",
        "max_length": 2000,
    },
    "pickup": {
        "label": "📦 Retrait",
        "column": "pickup",
        "max_length": 2000,
    },
    "contact": {
        "label": "📞 Contact",
        "column": "contact",
        "max_length": 2000,
    },
    "additional": {
        "label": "➕ Informations supplémentaires",
        "column": "additional",
        "max_length": 4000,
    },
}


def admin_information_keyboard(information: Information):
    buttons = []

    for field_name, field in INFORMATION_FIELDS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {field['label']}",
                callback_data=(
                    f"admin_information_edit:"
                    f"{information.id}:"
                    f"{field_name}"
                ),
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=(
                "🔴 Désactiver"
                if information.is_active
                else "🟢 Activer"
            ),
            callback_data=(
                f"admin_information_toggle:{information.id}"
            ),
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="🔄 Actualiser",
            callback_data="admin_information",
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Administration",
            callback_data="admin_home",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


async def get_or_create_information():
    async with AsyncSessionLocal() as session:
        information = await session.scalar(
            select(Information)
            .order_by(Information.id.asc())
        )

        if information is None:
            information = Information(
                title="INFORMATIONS",
                content="",
                presentation="",
                address="",
                opening_hours="",
                payment="",
                pickup="",
                contact="",
                additional="",
                is_active=True,
            )

            session.add(information)
            await session.commit()
            await session.refresh(information)

        return information


def information_admin_text(
    information: Information,
) -> str:
    status = (
        "🟢 ACTIF"
        if information.is_active
        else "🔴 INACTIF"
    )

    return f"""
ℹ️ <b>INFORMATIONS</b>

🆔 ID : <code>{information.id}</code>

📌 <b>Titre :</b>
{information.title}

━━━━━━━━━━━━━━━━━━

📝 <b>Présentation :</b>
{information.presentation or "—"}

📍 <b>Adresse :</b>
{information.address or "—"}

🕐 <b>Horaires :</b>
{information.opening_hours or "—"}

💶 <b>Paiement :</b>
{information.payment or "—"}

📦 <b>Retrait :</b>
{information.pickup or "—"}

📞 <b>Contact :</b>
{information.contact or "—"}

➕ <b>Informations supplémentaires :</b>
{information.additional or "—"}

━━━━━━━━━━━━━━━━━━

📊 <b>Statut :</b> {status}
"""


@router.callback_query(
    lambda callback: callback.data == "admin_information"
)
async def admin_information_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    information = await get_or_create_information()

    await callback.answer()

    try:
        await callback.message.edit_text(
            information_admin_text(information),
            reply_markup=admin_information_keyboard(
                information
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise


# ============================================================
# INFORMATIONS — MODIFIER UNE RUBRIQUE
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_information_edit:"
    )
)
async def admin_information_edit_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer(
            "❌ Action invalide.",
            show_alert=True,
        )
        return

    try:
        information_id = int(parts[1])
    except ValueError:
        await callback.answer(
            "❌ Information invalide.",
            show_alert=True,
        )
        return

    field_name = parts[2]

    if field_name not in INFORMATION_FIELDS:
        await callback.answer(
            "❌ Rubrique invalide.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        information = await session.scalar(
            select(Information).where(
                Information.id == information_id
            )
        )

        if information is None:
            await callback.answer(
                "❌ Information introuvable.",
                show_alert=True,
            )
            return

        field = INFORMATION_FIELDS[field_name]
        current_value = getattr(
            information,
            field["column"],
            "",
        )

    await state.clear()

    await state.update_data(
        information_id=information_id,
        field_name=field_name,
    )

    await state.set_state(
        InformationStates.waiting_field
    )

    await callback.answer()

    await callback.message.edit_text(
        f"""
✏️ <b>MODIFIER {field["label"].upper()}</b>

Valeur actuelle :
<code>{current_value or "Vide"}</code>

Écris maintenant la nouvelle valeur.

Tu peux utiliser plusieurs lignes.

❌ Pour annuler :
/cancel
"""
    )


@router.message(
    InformationStates.waiting_field
)
async def admin_information_field_message(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    if not message.text:
        await message.answer(
            "❌ La valeur doit être un texte."
        )
        return

    if message.text.strip() == "/cancel":
        await state.clear()

        await message.answer(
            "❌ Modification annulée.",
            reply_markup=admin_main_keyboard(),
        )
        return

    data = await state.get_data()

    information_id = data.get(
        "information_id"
    )
    field_name = data.get(
        "field_name"
    )

    if not information_id or field_name not in INFORMATION_FIELDS:
        await state.clear()

        await message.answer(
            "❌ Modification invalide.",
            reply_markup=admin_main_keyboard(),
        )
        return

    field = INFORMATION_FIELDS[field_name]
    value = message.text.strip()

    if len(value) > field["max_length"]:
        await message.answer(
            f"❌ Texte trop long.\n"
            f"Maximum : {field['max_length']} caractères."
        )
        return

    async with AsyncSessionLocal() as session:
        information = await session.scalar(
            select(Information).where(
                Information.id == information_id
            )
        )

        if information is None:
            await state.clear()

            await message.answer(
                "❌ Information introuvable.",
                reply_markup=admin_main_keyboard(),
            )
            return

        setattr(
            information,
            field["column"],
            value,
        )

        await session.commit()

    await state.clear()

    await message.answer(
        f"""
✅ <b>INFORMATION MODIFIÉE</b>

{field["label"]}

La modification a bien été enregistrée.
""",
        reply_markup=admin_main_keyboard(),
    )


# ============================================================
# INFORMATIONS — ACTIVER / DÉSACTIVER
# ============================================================

@router.callback_query(
    lambda callback: callback.data.startswith(
        "admin_information_toggle:"
    )
)
async def admin_information_toggle_callback(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Accès refusé.",
            show_alert=True,
        )
        return

    try:
        information_id = int(
            callback.data.split(":")[1]
        )
    except (ValueError, IndexError):
        await callback.answer(
            "❌ Information invalide.",
            show_alert=True,
        )
        return

    async with AsyncSessionLocal() as session:
        information = await session.scalar(
            select(Information).where(
                Information.id == information_id
            )
        )

        if information is None:
            await callback.answer(
                "❌ Information introuvable.",
                show_alert=True,
            )
            return

        information.is_active = (
            not information.is_active
        )

        new_status = information.is_active

        await session.commit()

    await callback.answer(
        "🟢 Informations activées."
        if new_status
        else "🔴 Informations désactivées."
    )

    information = await get_or_create_information()

    await callback.message.edit_text(
        information_admin_text(information),
        reply_markup=admin_information_keyboard(
            information
        ),
    )


# ============================================================
# INFORMATIONS — ANNULER
# ============================================================

@router.message(Command("cancel"))
async def admin_information_cancel_command(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    current_state = await state.get_state()

    if current_state != InformationStates.waiting_field.state:
        return

    await state.clear()

    await message.answer(
        "❌ Modification annulée.",
        reply_markup=admin_main_keyboard(),
    )

