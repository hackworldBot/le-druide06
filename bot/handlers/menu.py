from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import func, select

from bot.keyboards.main import main_menu_keyboard
from bot.keyboards.common import back_to_menu_keyboard
from bot.states.support import SupportStates
from bot.keyboards.support import support_keyboard

from database.database import AsyncSessionLocal
from database.models import (
    Cart,
    CartItem,
    Order,
    User,
    SupportTicket,
    SupportMessage,
    Information,
    Promotion,
)


router = Router()


MAIN_MENU_TEXT = """
🏠    MENU PRINCIPAL

Bienvenue dans notre boutique ! 🛍️

Que souhaitez-vous faire ?
"""


@router.callback_query(lambda callback: callback.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery):
    await callback.answer()

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=MAIN_MENU_TEXT,
            reply_markup=main_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            MAIN_MENU_TEXT,
            reply_markup=main_menu_keyboard(),
        )


@router.callback_query(lambda callback: callback.data == "menu_account")
async def account_menu_handler(callback: CallbackQuery):
    await callback.answer()

    telegram_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        user = await session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            error_text = (
                "❌ Compte introuvable \n\n"
                "Veuillez utiliser /start puis accepter les conditions."
            )

            if callback.message.photo:
                await callback.message.edit_caption(
                    caption=error_text,
                    reply_markup=back_to_menu_keyboard(),
                )
            else:
                await callback.message.edit_text(
                    error_text,
                    reply_markup=back_to_menu_keyboard(),
                )
            return

        total_orders = await session.scalar(
            select(func.count(Order.id)).where(
                Order.user_id == user.id
            )
        ) or 0

        active_orders = await session.scalar(
            select(func.count(Order.id)).where(
                Order.user_id == user.id,
                Order.status.notin_(
                    ("COMPLETED", "CANCELLED")
                ),
            )
        ) or 0

        completed_orders = await session.scalar(
            select(func.count(Order.id)).where(
                Order.user_id == user.id,
                Order.status == "COMPLETED",
            )
        ) or 0

        total_spent = await session.scalar(
            select(
                func.coalesce(
                    func.sum(Order.total),
                    0,
                )
            ).where(
                Order.user_id == user.id,
                Order.status == "COMPLETED",
            )
        ) or 0

        cart = await session.scalar(
            select(Cart).where(
                Cart.user_id == user.id
            )
        )

        cart_items = 0

        if cart is not None:
            cart_items = await session.scalar(
                select(
                    func.coalesce(
                        func.sum(CartItem.quantity),
                        0,
                    )
                ).where(
                    CartItem.cart_id == cart.id
                )
            ) or 0

    username = (
        f"@{user.username}"
        if user.username
        else "Non renseigné"
    )

    full_name = " ".join(
        part
        for part in (
            user.first_name,
            user.last_name,
        )
        if part
    ) or "Non renseigné"

    accepted_text = (
        "✅ Acceptées"
        if user.accepted
        else "❌ Non acceptées"
    )

    account_status = (
        "🔴 Bloqué"
        if user.is_blocked
        else "🟢 Actif"
    )

    account_text = f"""
👤    MON COMPTE

👤 Informations personnelles

Nom : {full_name}
Username : {username}
🆔 ID Telegram : {user.telegram_id}

📅 Compte

Date d'inscription : {user.created_at:%d/%m/%Y}
Conditions : {accepted_text}
Statut : {account_status}

📦 Commandes

Total :   {total_orders}
En cours :   {active_orders}
Terminées :   {completed_orders}

💰 Achats

Total dépensé : {total_spent:.2f} €

🛒 Panier

Articles actuellement dans le panier : {cart_items}
"""

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=account_text,
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            account_text,
            reply_markup=back_to_menu_keyboard(),
        )


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
                    text="💳 Question paiement",
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


@router.callback_query(
    lambda callback: callback.data == "menu_support"
)
async def support_menu_handler(callback: CallbackQuery):
    await callback.answer()

    text = """
💬    SUPPORT — LE DRUIDE 06

Bienvenue dans notre espace support.

Choisissez le sujet de votre demande :
"""

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=support_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=support_keyboard(),
        )


SUPPORT_TOPICS = {
    "support_order": "📦 Problème avec une commande",
    "support_product": "🛍️ Question sur un produit",
    "support_payment": "💳 Question paiement",
    "support_other": "📝 Autre demande",
}


@router.callback_query(
    lambda callback: callback.data in SUPPORT_TOPICS
)
async def support_topic_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()

    topic = SUPPORT_TOPICS[callback.data]

    await state.update_data(support_topic=topic)
    await state.set_state(SupportStates.waiting_message)

    text = f"""
💬    SUPPORT

Sujet : {topic}

✍️ Écrivez maintenant votre message.

Notre équipe vous répondra dès que possible.
"""

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=back_to_menu_keyboard(),
        )


@router.message(SupportStates.waiting_message)
async def support_message_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    topic = data.get(
        "support_topic",
        "📝 Autre demande",
    )

    telegram_id = message.from_user.id
    message_text = (
        message.text
        or message.caption
        or "Message non textuel"
    )

    async with AsyncSessionLocal() as session:
        # Recherche de l'utilisateur par son Telegram ID
        user = await session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            await state.clear()

            await message.answer(
                """
❌   COMPTE INTROUVABLE

Impossible d'associer votre demande à votre compte.

Veuillez utiliser /start puis réessayer.
""",
                reply_markup=back_to_menu_keyboard(),
            )
            return

        # Création du ticket
        ticket = SupportTicket(
            user_id=user.id,
            topic=topic,
            status="OPEN",
        )

        session.add(ticket)
        await session.flush()

        # Premier message du ticket
        support_message = SupportMessage(
            ticket_id=ticket.id,
            sender_type="USER",
            sender_telegram_id=telegram_id,
            message=message_text,
        )

        session.add(support_message)

        await session.commit()
        await session.refresh(ticket)

        ticket_id = ticket.id

    await state.clear()

    # Notification simple de l'administrateur
    admin_id = 8727592009

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Non renseigné"
    )

    admin_text = f"""
💬    NOUVEAU TICKET SUPPORT

🆔 Ticket : #{ticket_id}

📌 Sujet :
{topic}

👤 Client :
{message.from_user.first_name or "Non renseigné"}

🔗 Username :
{username}

🆔 Telegram ID :
{telegram_id}

━━━━━━━━━━━━━━━━━━

📝 Message :

{message_text}

━━━━━━━━━━━━━━━━━━

👉 Ouvre le panneau
💬 Support dans /admin
pour répondre au client.
"""

    try:
        await message.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
        )
    except Exception:
        # Le ticket est déjà enregistré en base.
        # Une erreur de notification Telegram ne doit
        # pas annuler la demande du client.
        pass

    await message.answer(
        f"""
✅    DEMANDE ENREGISTRÉE

Votre demande a bien été transmise à notre équipe.

🆔 Numéro de ticket :
#{ticket_id}

Nous reviendrons vers vous dès que possible. 🙏
""",
        reply_markup=back_to_menu_keyboard(),
    )


@router.callback_query(
    lambda callback: callback.data == "menu_information"
)
async def information_menu_handler(
    callback: CallbackQuery,
):
    await callback.answer()

    async with AsyncSessionLocal() as session:
        information = await session.scalar(
            select(Information)
            .where(Information.is_active.is_(True))
            .order_by(Information.id.asc())
        )

        # Création automatique d'une fiche par défaut
        # si aucune information n'existe encore.
        if information is None:
            information = Information(
                title="INFORMATIONS",
                content=(
                    "🛍️ Boutique\n"
                    "💵 Paiement en liquide sur place\n"
                    "📦 Retrait directement en boutique\n\n"
                    "Merci de votre confiance !"
                ),
                is_active=True,
            )

            session.add(information)
            await session.commit()
            await session.refresh(information)

    information_text = f"""
ℹ️    {information.title}

{information.content}
"""

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=information_text,
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            information_text,
            reply_markup=back_to_menu_keyboard(),
        )


@router.message(Command("boutique"))
async def boutique_command_handler(message: Message):
    await message.answer(
        """
🛍️    BOUTIQUE

Utilisez le bouton ci-dessous pour accéder à la boutique.
""",
        reply_markup=main_menu_keyboard(),
    )


# ============================================================
# PROMOTIONS UTILISATEUR
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "menu_promotions"
)
async def promotions_menu_handler(
    callback: CallbackQuery,
):
    await callback.answer()

    async with AsyncSessionLocal() as session:
        promotion = await session.scalar(
            select(Promotion)
            .where(Promotion.is_active.is_(True))
            .order_by(Promotion.id.asc())
        )

    if promotion is None:
        promotions_text = """
🏷️    PROMOTIONS

Aucune promotion n'est actuellement disponible.

Revenez bientôt ! 😊
"""
    else:
        content = promotion.content.strip()

        if not content:
            content = "Aucune promotion disponible actuellement."

        promotions_text = f"""
🏷️    {promotion.title}

{content}
"""

    if callback.message.photo:
        await callback.message.edit_caption(
            caption=promotions_text,
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            promotions_text,
            reply_markup=back_to_menu_keyboard(),
        )
