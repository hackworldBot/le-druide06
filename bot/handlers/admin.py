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
from bot.filters.admin import AdminFilter

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
    ProductVariant,
)

from bot.states.admin import (
    ProductStates,
    CategoryStates,
    InformationStates,
    PromotionStates,
    UserStates,
)
from bot.states.support import SupportStates

from bot.keyboards.admin_products import (
    admin_products_keyboard,
    admin_product_list_keyboard,
    admin_product_detail_keyboard,
    admin_variants_keyboard,
    admin_variant_list_keyboard,
)

from bot.keyboards.admin import (
    admin_main_keyboard,
    admin_orders_keyboard,
    admin_order_detail_keyboard,
    admin_category_list_keyboard,
    admin_category_detail_keyboard,
)


router = Router()

router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())





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
👨‍💼    ADMINISTRATION

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
👨‍💼    ADMINISTRATION

📦 Commandes : {len(orders)}

🟡 En attente : {pending}
🔵 En préparation : {preparing}
🟢 Prêtes : {ready}
✅ Terminées : {completed}
🔴 Annulées : {cancelled}

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


@router.message(AdminFilter(), Command("admin"))
async def admin_command(message: Message):
    await show_admin_home(message)


async def show_admin_home(target):
    text = """
👨‍💼    ADMINISTRATION

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
    AdminFilter(),
    lambda callback: callback.data == "admin_home"
)
async def admin_home_callback(callback: CallbackQuery):
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
📦    GESTION DES PRODUITS

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
    AdminFilter(),
    lambda callback: callback.data == "admin_products"
)
async def admin_products_callback(callback: CallbackQuery):
    await callback.answer()
    await show_admin_products(callback)


@router.callback_query(
    AdminFilter(),
    lambda callback: callback.data == "admin_product_add"
)
async def admin_product_add_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await state.set_state(ProductStates.waiting_name)

    await callback.answer()

    await callback.message.edit_text(
        """
➕    AJOUT D'UN PRODUIT

Entrez le nom du produit :
"""
    )


@router.callback_query(
    lambda callback: callback.data == "admin_product_list"
)
async def admin_product_list_callback(callback: CallbackQuery):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .order_by(Product.name)
        )

        products = result.scalars().all()

    if not products:
        text = """
📋    LISTE DES PRODUITS

Aucun produit dans la base.
"""
    else:
        text = """
📋    LISTE DES PRODUITS

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
📦    PRODUIT #{product.id}

{product.name}

📝 Description :
{product.description or "Aucune description"}

💰 Prix : {product.price:.2f} €
📊 Stock : {product.stock}
📂 Catégorie : {category_name}
📌 Statut : {status}
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

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category)
            .order_by(Category.sort_order, Category.name)
        )
        categories = result.scalars().all()

    if not categories:
        text = """
📂    GESTION DES CATÉGORIES

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

    await state.clear()
    await state.set_state(CategoryStates.waiting_name)

    await callback.answer()

    await callback.message.edit_text(
        """
➕    AJOUT D'UNE CATÉGORIE

Entrez le nom de la catégorie :

Exemple :
Boissons
"""
    )


@router.message(CategoryStates.waiting_name)
async def category_waiting_name(
    message: Message,
    state: FSMContext,
):

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
📝    DESCRIPTION

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
🔢    ORDRE D'AFFICHAGE

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
✅    CATÉGORIE CRÉÉE

📂 {category.name}

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : {category.sort_order}

📌 Statut : 🟢 ACTIF

🆔 ID : #{category.id}
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

    await callback.answer()
    await show_admin_orders(callback)


@router.callback_query(
    lambda callback: callback.data.startswith("admin_order:")
)
async def admin_order_detail(callback: CallbackQuery):

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
        f"👨‍💼 COMMANDE #{order.id}",
        "",
        f"📅 {order.created_at:%d/%m/%Y %H:%M}",
        f"📌 Statut : {status_label(order.status)}",
        f"💰 Total : {order.total:.2f} €",
        f"💵 Paiement : {order.payment_method}",
        "",
        "📦 ARTICLES",
        "",
    ]

    for item in items:
        lines.append(
            f"• {item.product_name} "
            f"x{item.quantity} "
            f"= {item.subtotal:.2f} €"
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
        "📝 DESCRIPTION\n\n"
        "Entrez la description du produit.\n\n"
        "Si vous ne voulez pas de description, envoyez :\n"
        "<code>-</code>"
    )


@router.message(ProductStates.waiting_description)
async def product_waiting_description(
    message: Message,
    state: FSMContext,
):

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
    await state.set_state(ProductStates.waiting_photo)

    await message.answer(
        "📷 PHOTO DU PRODUIT\n\n"
        "Envoyez une photo du produit."
    )




@router.message(ProductStates.waiting_photo)
async def product_waiting_photo(
    message: Message,
    state: FSMContext,
):
    if not message.photo:
        await message.answer(
            "❌ Envoyez une photo Telegram."
        )
        return

    photo_id = message.photo[-1].file_id

    await state.update_data(image=photo_id)
    await state.set_state(ProductStates.waiting_video)

    await message.answer(
        "🎥 VIDÉO DU PRODUIT\n\n"
        "Envoyez une vidéo ou tapez - pour ignorer."
    )


@router.message(ProductStates.waiting_video)
async def product_waiting_video(
    message: Message,
    state: FSMContext,
):
    video_id = None

    if message.text and message.text.strip() == "-":
        pass

    elif message.video:
        video_id = message.video.file_id

    else:
        await message.answer(
            "❌ Envoyez une vidéo ou tapez -"
        )
        return

    await state.update_data(video=video_id)
    await state.set_state(ProductStates.waiting_price)

    await message.answer(
        "💰 PRIX\n\n"
        "Entrez le prix en euros.\n\n"
        "Exemple : <code>12.50</code>"
    )


@router.message(ProductStates.waiting_price)
async def product_waiting_price(
    message: Message,
    state: FSMContext,
):

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
        "📊 STOCK\n\n"
        "Entrez la quantité disponible.\n\n"
        "Exemple : <code>10</code>"
    )


@router.message(ProductStates.waiting_stock)
async def product_waiting_stock(
    message: Message,
    state: FSMContext,
):

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
    await state.set_state(ProductStates.waiting_product_type)

    await message.answer(
        "📦 TYPE DE PRODUIT \n\n"
        "Tapez :\n\n"
        "physical = produit physique\n"
        "digital = produit numérique"
    )
    
@router.message(ProductStates.waiting_product_type)
async def product_waiting_product_type(
    message: Message,
    state: FSMContext,
):
    value = message.text.strip().lower()

    if value not in ("physical", "digital"):
        await message.answer(
            "❌ Valeur invalide.\n\n"
            "Répondez : physical ou digital"
        )
        return

    await state.update_data(product_type=value)
    await state.set_state(ProductStates.waiting_sku)

    await message.answer(
        "🏷️ SKU (optionnel)\n\n"
        "Envoyez un SKU ou - pour ignorer."
    )


@router.message(ProductStates.waiting_sku)
async def product_waiting_sku(
    message: Message,
    state: FSMContext,
):
    sku = message.text.strip()

    if sku == "-":
        sku = None

    await state.update_data(sku=sku)
    await state.set_state(ProductStates.waiting_download_link)

    await message.answer(
        "🔗 Lien de téléchargement\n\n"
        "Pour un produit physique tapez -\n"
        "Pour un produit numérique collez l'URL."
    )


@router.message(ProductStates.waiting_download_link)
async def product_waiting_download_link(
    message: Message,
    state: FSMContext,
):
    link = message.text.strip()

    if link == "-":
        link = None

    await state.update_data(download_link=link)
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
        "📂 CATÉGORIE\n\n"
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
            sku=data.get("sku"),
            product_type=data.get("product_type", "physical"),
            name=data["name"],
            description=data.get("description"),
            price=Decimal(data["price"]),
            stock=data["stock"],
            sold_count=0,
            image=data.get("image"),
            video=data.get("video"),
            download_link=data.get("download_link"),
            created_by=callback.from_user.id,
            updated_by=callback.from_user.id,
            is_active=True,
        )

        session.add(product)
        await session.commit()
        await session.refresh(product)

    await state.clear()

    await callback.answer("✅ Produit créé !")

    await callback.message.edit_text(
        f"""
✅ PRODUIT CRÉÉ

📦 {product.name}

📝 Description :
{product.description or "Aucune description"}

💰 Prix : {product.price:.2f} €
📊 Stock : {product.stock}
📂 Catégorie : {category.name}
📌 Statut : 🟢 ACTIF

🆔 ID : #{product.id}
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
✏️ MODIFICATION DU PRODUIT #{product.id}

Nom actuel :
{product.name}

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
📝 DESCRIPTION

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
💰    PRIX

Prix actuel :
{product.price:.2f} €

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
📊 STOCK

Stock actuel :
{product.stock}

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
✅ PRODUIT MODIFIÉ

📦 {product.name}

📝 Description :
{product.description or "Aucune description"}

💰 Prix : {product.price:.2f} €
📊 Stock : {product.stock}
📂 Catégorie : {category_name}
📌 Statut :
{"🟢 ACTIF" if product.is_active else "🔴 INACTIF"}

🆔 ID : #{product.id}
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
💰 MODIFIER LE PRIX

Produit :
{product.name}

Prix actuel :
{product.price:.2f} €

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
📊 MODIFIER LE STOCK

Produit :
{product.name}

Stock actuel :
{product.stock}

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
📦 PRODUIT #{product.id}

{product.name}

📝 Description :
{product.description or "Aucune description"}

💰 Prix : {product.price:.2f} €
📊 Stock : {product.stock}
📂 Catégorie : {category.name if category else "Inconnue"}
📌 Statut : {status}
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
📂 CATÉGORIE #{category.id}

{category.name}

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : {category.sort_order}
📌 Statut : {status}
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
📂 CATÉGORIE #{category.id}

{category.name}

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : {category.sort_order}
📌 Statut : {status_label}
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
✏️ MODIFICATION CATÉGORIE #{category.id}

Nom actuel :
{category.name}

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
📝 DESCRIPTION

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
🔢 ORDRE D'AFFICHAGE

Ordre actuel :
{category.sort_order}

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
✅ CATÉGORIE MODIFIÉE

📂 {category.name}

📝 Description :
{category.description or "Aucune description"}

🔢 Ordre : {category.sort_order}
📌 Statut : {status}

🆔 ID : #{category.id}
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
⚠️ SUPPRESSION IMPOSSIBLE

📂 Catégorie :
{category.name}

Cette catégorie contient actuellement
{len(products)} produit(s).

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
⚠️ CONFIRMATION DE SUPPRESSION

Voulez-vous vraiment supprimer :

📂 {category.name}

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
✅ CATÉGORIE SUPPRIMÉE

La catégorie
{category_name}
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
        title = "🟠 TICKETS OUVERTS"
    elif status_filter == "IN_PROGRESS":
        title = "🔵 TICKETS EN COURS"
    else:
        title = "📋 TOUS LES TICKETS"

    if not tickets:
        text = f"""
💬 SUPPORT

{title}

Aucun ticket dans cette catégorie.
"""
    else:
        lines = [
            "💬 SUPPORT",
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
                f"{icon} #{ticket.id} — "
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
        "💬 TICKET SUPPORT",
        "",
        f"🆔 Ticket : #{ticket.id}",
        f"📌 Sujet : {ticket.topic}",
        f"📊 Statut : {status}",
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
                f"{sender}"
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
💬 RÉPONSE AU TICKET #{ticket.id}

📌 Sujet :
{ticket.topic}

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
💬 RÉPONSE DU SUPPORT

🆔 Ticket : #{ticket_id}

📌 Sujet :
{ticket.topic}

━━━━━━━━━━━━━━━━━━

{reply_text}

━━━━━━━━━━━━━━━━━━

🙏 Merci pour votre patience.
""",
        )
    except Exception as error:
        await message.answer(
            f"""
⚠️ RÉPONSE ENREGISTRÉE MAIS NON ENVOYÉE

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
✅ RÉPONSE ENVOYÉE

Votre réponse a été envoyée au client.

🆔 Ticket :
#{ticket_id}

📊 Statut :
🔵 EN COURS
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
ℹ️ INFORMATIONS

🆔 ID : <code>{information.id}</code>

📌 Titre :
{information.title}

━━━━━━━━━━━━━━━━━━

📝 Présentation :
{information.presentation or "—"}

📍 Adresse :
{information.address or "—"}

🕐 Horaires :
{information.opening_hours or "—"}

💶 Paiement :
{information.payment or "—"}

📦 Retrait :
{information.pickup or "—"}

📞 Contact :
{information.contact or "—"}

➕ Informations supplémentaires :
{information.additional or "—"}

━━━━━━━━━━━━━━━━━━

📊 Statut :{status}
"""


@router.callback_query(
    lambda callback: callback.data == "admin_information"
)
async def admin_information_callback(
    callback: CallbackQuery,
):

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
✏️ MODIFIER {field["label"].upper()}

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
✅ INFORMATION MODIFIÉE

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
# PROMOTIONS ADMIN
# ============================================================

def promotion_admin_text(promotion: Promotion) -> str:
    status = "🟢 ACTIVÉE" if promotion.is_active else "🔴 DÉSACTIVÉE"

    content = promotion.content.strip()

    if not content:
        content = "Aucune promotion configurée."

    return f"""
🏷️ PROMOTIONS

Statut : {status}

Titre :
{promotion.title}

Contenu :
{content}
"""


def promotion_admin_keyboard(
    promotion: Promotion,
) -> InlineKeyboardMarkup:
    status_text = (
        "🔴 Désactiver"
        if promotion.is_active
        else "🟢 Activer"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Modifier le titre",
                    callback_data="admin_promotion_title",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Modifier le contenu",
                    callback_data="admin_promotion_content",
                )
            ],
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data="admin_promotion_toggle",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Actualiser",
                    callback_data="admin_promotions",
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

@router.callback_query(
    lambda callback: callback.data == "admin_users"
)
async def admin_users_callback(callback: CallbackQuery):
    await callback.answer()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(20)
        )

        users = result.scalars().all()

    lines = [
        "👥 <b>UTILISATEURS</b>",
        "",
        f"Total affiché : {len(users)}",
        "",
    ]

    if not users:
        lines.append("Aucun utilisateur enregistré.")
    else:
        for user in users:
            username = (
                f"@{user.username}"
                if user.username
                else "Aucun pseudo"
            )

            lines.append(
                f"• {user.first_name or 'Sans nom'} "
                f"({username})"
            )

            lines.append(
                f"ID : <code>{user.telegram_id}</code>"
            )

            lines.append("")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistiques",
                    callback_data="admin_users_stats",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Recherche ID",
                    callback_data="admin_users_search",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅ Retour",
                    callback_data="admin_home",
                )
            ]
        ]
    )

    await callback.message.answer(
        "\n".join(lines),
        reply_markup=keyboard,
    )

async def get_or_create_promotion():
    async with AsyncSessionLocal() as session:
        promotion = await session.scalar(
            select(Promotion)
            .order_by(Promotion.id.asc())
        )

        if promotion is None:
            promotion = Promotion(
                title="PROMOTIONS",
                content="",
                is_active=False,
            )

            session.add(promotion)
            await session.commit()
            await session.refresh(promotion)

        return promotion


# ============================================================
# PROMOTIONS — OUVRIR
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "admin_promotions"
)
async def admin_promotions_callback(
    callback: CallbackQuery,
):

    promotion = await get_or_create_promotion()

    await callback.answer()

    try:
        await callback.message.edit_text(
            promotion_admin_text(promotion),
            reply_markup=promotion_admin_keyboard(
                promotion
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise


# ============================================================
# PROMOTIONS — MODIFIER LE TITRE
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "admin_promotion_title"
)
async def admin_promotion_title_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    promotion = await get_or_create_promotion()

    await state.set_state(
        PromotionStates.waiting_title
    )

    await callback.answer()

    await callback.message.answer(
        f"""
✏️ MODIFIER LE TITRE<

Titre actuel :
{promotion.title}

Envoie le nouveau titre.

Maximum : 255 caractères.

/cancel pour annuler.
"""
    )


# ============================================================
# PROMOTIONS — ENREGISTRER LE TITRE
# ============================================================

@router.message(
    PromotionStates.waiting_title
)
async def admin_promotion_title_message(
    message: Message,
    state: FSMContext,
):

    value = (message.text or "").strip()

    if not value:
        await message.answer(
            "❌ Le titre ne peut pas être vide."
        )
        return

    if len(value) > 255:
        await message.answer(
            "❌ Titre trop long.\n"
            "Maximum : 255 caractères."
        )
        return

    promotion = await get_or_create_promotion()

    async with AsyncSessionLocal() as session:
        promotion_db = await session.scalar(
            select(Promotion).where(
                Promotion.id == promotion.id
            )
        )

        if promotion_db is None:
            await state.clear()

            await message.answer(
                "❌ Promotion introuvable.",
                reply_markup=admin_main_keyboard(),
            )
            return

        promotion_db.title = value
        await session.commit()

    await state.clear()

    promotion = await get_or_create_promotion()

    await message.answer(
        promotion_admin_text(promotion),
        reply_markup=promotion_admin_keyboard(
            promotion
        ),
    )


# ============================================================
# PROMOTIONS — MODIFIER LE CONTENU
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "admin_promotion_content"
)
async def admin_promotion_content_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    await get_or_create_promotion()

    await state.set_state(
        PromotionStates.waiting_content
    )

    await callback.answer()

    await callback.message.answer(
        """
📝 MODIFIER LA PROMOTION

Envoie le texte de la promotion qui sera affiché aux clients.

Tu peux utiliser plusieurs lignes.

Maximum : 4000 caractères.

/cancel pour annuler.
"""
    )


# ============================================================
# PROMOTIONS — ENREGISTRER LE CONTENU
# ============================================================

@router.message(
    PromotionStates.waiting_content
)
async def admin_promotion_content_message(
    message: Message,
    state: FSMContext,
):

    value = (message.text or "").strip()

    if not value:
        await message.answer(
            "❌ Le contenu ne peut pas être vide."
        )
        return

    if len(value) > 4000:
        await message.answer(
            "❌ Contenu trop long.\n"
            "Maximum : 4000 caractères."
        )
        return

    promotion = await get_or_create_promotion()

    async with AsyncSessionLocal() as session:
        promotion_db = await session.scalar(
            select(Promotion).where(
                Promotion.id == promotion.id
            )
        )

        if promotion_db is None:
            await state.clear()

            await message.answer(
                "❌ Promotion introuvable.",
                reply_markup=admin_main_keyboard(),
            )
            return

        promotion_db.content = value
        await session.commit()

    await state.clear()

    promotion = await get_or_create_promotion()

    await message.answer(
        promotion_admin_text(promotion),
        reply_markup=promotion_admin_keyboard(
            promotion
        ),
    )


# ============================================================
# PROMOTIONS — ACTIVER / DÉSACTIVER
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "admin_promotion_toggle"
)
async def admin_promotion_toggle_callback(
    callback: CallbackQuery,
):

    promotion = await get_or_create_promotion()

    async with AsyncSessionLocal() as session:
        promotion_db = await session.scalar(
            select(Promotion).where(
                Promotion.id == promotion.id
            )
        )

        if promotion_db is None:
            await callback.answer(
                "❌ Promotion introuvable.",
                show_alert=True,
            )
            return

        promotion_db.is_active = not promotion_db.is_active
        new_status = promotion_db.is_active

        await session.commit()

    await callback.answer(
        "🟢 Promotions activées."
        if new_status
        else "🔴 Promotions désactivées."
    )

    promotion = await get_or_create_promotion()

    try:
        await callback.message.edit_text(
            promotion_admin_text(promotion),
            reply_markup=promotion_admin_keyboard(
                promotion
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise


# ============================================================
# PROMOTIONS — ANNULER
# ============================================================

@router.message(PromotionStates.waiting_title)
@router.message(PromotionStates.waiting_content)
async def admin_promotion_cancel_command(
    message: Message,
    state: FSMContext,
):

    if (message.text or "").strip().lower() != "/cancel":
        return

    await state.clear()

    await message.answer(
        "❌ Modification annulée.",
        reply_markup=admin_main_keyboard(),
    )

@router.callback_query(
    lambda callback: callback.data == "admin_users_stats"
)
async def admin_users_stats_callback(callback: CallbackQuery):
    await callback.answer()

    async with AsyncSessionLocal() as session:
        users = (
            await session.execute(select(User))
        ).scalars().all()

    total_users = len(users)
    accepted_users = len(
        [u for u in users if u.accepted]
    )
    blocked_users = len(
        [u for u in users if u.is_blocked]
    )

    text = f"""
📊 <b>STATISTIQUES UTILISATEURS</b>

👥 Total utilisateurs : {total_users}
✅ Conditions acceptées : {accepted_users}
🚫 Comptes bloqués : {blocked_users}
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅ Retour utilisateurs",
                    callback_data="admin_users",
                )
            ]
        ]
    )

    await callback.message.answer(
        text,
        reply_markup=keyboard,
    )




@router.callback_query(
    lambda callback: callback.data == "admin_users_search"
)
async def admin_users_search_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()

    await state.set_state(
        UserStates.waiting_telegram_id
    )

    await callback.message.answer(
        "🔍 Envoyez l'ID Telegram de l'utilisateur :"
    )


@router.message(
    UserStates.waiting_telegram_id
)
async def admin_user_search_process(
    message: Message,
    state: FSMContext,
):
    try:
        telegram_id = int(message.text.strip())
    except Exception:
        await message.answer(
            "❌ ID invalide."
        )
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

    await state.clear()

    if not user:
        await message.answer(
            "❌ Utilisateur introuvable."
        )
        return

    username = (
        f"@{user.username}"
        if user.username
        else "Aucun pseudo"
    )

    status = (
        "🚫 Bloqué"
        if user.is_blocked
        else "✅ Actif"
    )

    text = f"""
👤 <b>UTILISATEUR</b>

Nom : {user.first_name or "Inconnu"}
Pseudo : {username}

ID :
<code>{user.telegram_id}</code>

Statut : {status}
Conditions :
{"✅ Acceptées" if user.accepted else "❌ Refusées"}
"""

    await message.answer(text)


@router.callback_query(
    lambda callback: callback.data == "admin_dashboard"
)
async def admin_dashboard_callback(
    callback: CallbackQuery,
):
    await callback.answer()

    async with AsyncSessionLocal() as session:

        users_count = len(
            (
                await session.execute(
                    select(User)
                )
            ).scalars().all()
        )

        products_count = len(
            (
                await session.execute(
                    select(Product)
                )
            ).scalars().all()
        )

        categories_count = len(
            (
                await session.execute(
                    select(Category)
                )
            ).scalars().all()
        )

        orders_count = len(
            (
                await session.execute(
                    select(Order)
                )
            ).scalars().all()
        )

        support_count = len(
            (
                await session.execute(
                    select(SupportTicket)
                )
            ).scalars().all()
        )

    text = f"""
📊 <b>TABLEAU DE BORD</b>

👥 Utilisateurs : {users_count}

📦 Produits : {products_count}

📂 Catégories : {categories_count}

🛒 Commandes : {orders_count}

🎟 Tickets support : {support_count}
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Actualiser",
                    callback_data="admin_dashboard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅ Administration",
                    callback_data="admin_home",
                )
            ]
        ]
    )

    await callback.message.answer(
        text,
        reply_markup=keyboard,
    )


@router.callback_query(
    lambda callback:
    callback.data.startswith("admin_product_delete:")
)
async def admin_product_delete_callback(
    callback: CallbackQuery,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirmer",
                    callback_data=f"confirm_delete_product:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Annuler",
                    callback_data=f"admin_product:{product_id}",
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "⚠️ Confirmer la suppression du produit ?",
        reply_markup=keyboard,
    )


@router.callback_query(
    lambda callback:
    callback.data.startswith("confirm_delete_product:")
)
async def confirm_delete_product_callback(
    callback: CallbackQuery,
):
    product_id = int(
        callback.data.split(":")[1]
    )

    async with AsyncSessionLocal() as session:
        product = await session.scalar(
            select(Product).where(
                Product.id == product_id
            )
        )

        if product is None:
            await callback.answer(
                "Produit introuvable",
                show_alert=True,
            )
            return

        await session.delete(product)
        await session.commit()

    await callback.answer(
        "✅ Produit supprimé"
    )

    await callback.message.edit_text(
        "✅ Produit supprimé avec succès."
    )


@router.callback_query(
    lambda callback: callback.data.startswith("admin_variants:")
)
async def debug_variants_log(callback: CallbackQuery):
    print("CALLBACK:", callback.data)

@router.callback_query(
    lambda callback: callback.data.startswith("admin_variants:")
)
async def admin_variants_callback(callback: CallbackQuery):

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

    await callback.answer()

    await callback.message.edit_text(
        f"""
🧩 GESTION DES VARIANTES

Produit :
{product.name}

Choisissez une action :
""",
        reply_markup=admin_variants_keyboard(product.id),
    )


@router.callback_query(
    lambda c: c.data.startswith("admin_variant_add:")
)
async def admin_variant_add_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    product_id = int(callback.data.split(":")[1])

    await state.update_data(
        variant_product_id=product_id
    )

    await state.set_state(
        ProductStates.waiting_variant_name
    )

    await callback.message.answer(
        "🧩 Nom de la variante ?"
    )

    await callback.answer()


@router.message(
    ProductStates.waiting_variant_name
)
async def variant_name_step(
    message: Message,
    state: FSMContext,
):
    await state.update_data(
        variant_name=message.text
    )

    await state.set_state(
        ProductStates.waiting_variant_price
    )

    await message.answer(
        "💰 Prix de la variante ?"
    )


@router.message(
    ProductStates.waiting_variant_price
)
async def variant_price_step(
    message: Message,
    state: FSMContext,
):
    await state.update_data(
        variant_price=message.text
    )

    await state.set_state(
        ProductStates.waiting_variant_stock
    )

    await message.answer(
        "📦 Stock de la variante ?"
    )


@router.message(
    ProductStates.waiting_variant_stock
)
async def variant_stock_step(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        variant = ProductVariant(
            product_id=data["variant_product_id"],
            name=data["variant_name"],
            price=data["variant_price"],
            stock=int(message.text),
        )

        session.add(variant)
        await session.commit()

    await state.clear()

    await message.answer(
        "✅ Variante ajoutée"
    )

@router.callback_query(
    lambda c: c.data.startswith("admin_variant_list:")
)
async def admin_variant_list_callback(
    callback: CallbackQuery,
):
    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ProductVariant)
            .where(ProductVariant.product_id == product_id)
            .order_by(ProductVariant.id)
        )

        variants = result.scalars().all()

    if not variants:
        text = """
📋 LISTE DES VARIANTES

Aucune variante enregistrée.
"""
    else:
        text = """
📋 LISTE DES VARIANTES

Cliquez sur une variante pour la supprimer :
"""

    await callback.answer()

    await callback.message.edit_text(
        text,
        reply_markup=admin_variant_list_keyboard(
            variants,
            product_id,
        ),
    )

