from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from bot.keyboards.orders import (
    order_detail_keyboard,
    orders_keyboard,
)
from bot.keyboards.common import back_to_menu_keyboard

from database.database import AsyncSessionLocal
from database.models import Order, OrderItem, User


router = Router()


STATUS_LABELS = {
    "PENDING": "🟡 EN ATTENTE",
    "PREPARING": "🔵 EN PRÉPARATION",
    "READY": "🟢 PRÊTE",
    "COMPLETED": "✅ TERMINÉE",
    "CANCELLED": "🔴 ANNULÉE",
}


def status_label(status: str) -> str:
    return STATUS_LABELS.get(
        status,
        f"⚪ {status}",
    )


async def get_user_orders(telegram_id: int):
    async with AsyncSessionLocal() as session:
        user = await session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            return None, []

        result = await session.execute(
            select(Order)
            .where(Order.user_id == user.id)
            .order_by(Order.created_at.desc())
        )

        return user, result.scalars().all()


async def show_orders(message: Message, telegram_id: int):
    user, orders = await get_user_orders(telegram_id)

    if user is None:
        await message.answer(
            "Veuillez utiliser /start puis accepter les conditions."
        )
        return

    active_orders = [
        order
        for order in orders
        if order.status not in ("COMPLETED", "CANCELLED")
    ]

    if not active_orders:
        await message.answer(
            """
📦 MES COMMANDES

Vous n'avez aucune commande en cours.

Rendez-vous dans 🛍️ Boutique pour commencer vos achats.
""",
            reply_markup=orders_keyboard([]),
        )
        return

    lines = [
        "📦 <b>MES COMMANDES</b>",
        "",
        "Voici vos commandes en cours :",
    ]

    await message.answer(
        "\n".join(lines),
        reply_markup=orders_keyboard(active_orders),
    )


@router.callback_query(
    lambda callback: callback.data == "menu_orders"
)
async def orders_handler(callback: CallbackQuery):
    await callback.answer()

    telegram_id = callback.from_user.id

    user, orders = await get_user_orders(telegram_id)

    if user is None:
        await callback.message.edit_text(
            "Veuillez utiliser /start puis accepter les conditions.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    active_orders = [
        order
        for order in orders
        if order.status not in ("COMPLETED", "CANCELLED")
    ]

    if not active_orders:
        await callback.message.edit_text(
            """
📦 MES COMMANDES

Vous n'avez aucune commande en cours.

Rendez-vous dans 🛍️ Boutique pour commencer vos achats.
""",
            reply_markup=orders_keyboard([]),
        )
        return

    await callback.message.edit_text(
        """
📦 MES COMMANDES

Sélectionnez une commande :
""",
        reply_markup=orders_keyboard(active_orders),
    )


@router.callback_query(
    lambda callback: callback.data == "menu_history"
)
async def history_handler(callback: CallbackQuery):
    await callback.answer()

    telegram_id = callback.from_user.id

    user, orders = await get_user_orders(telegram_id)

    if user is None:
        await callback.message.edit_text(
            "Veuillez utiliser /start puis accepter les conditions.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    history_orders = [
        order
        for order in orders
        if order.status in ("COMPLETED", "CANCELLED")
    ]

    if not history_orders:
        await callback.message.edit_text(
            """
🕘 HISTORIQUE

Votre historique de commandes est vide.
""",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    lines = [
        "🕘 <b>HISTORIQUE DES COMMANDES</b>",
        "",
    ]

    for order in history_orders:
        lines.append(
            f"📦 <b>Commande #{order.id}</b>\n"
            f"   📅 {order.created_at:%d/%m/%Y %H:%M}\n"
            f"   💰 {order.total:.2f} €\n"
            f"   {status_label(order.status)}"
        )

        lines.append("")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_menu_keyboard(),
    )


@router.callback_query(
    lambda callback: callback.data.startswith("order:")
)
async def order_detail_handler(callback: CallbackQuery):
    try:
        order_id = int(
            callback.data.split(":")[1]
        )
    except (IndexError, ValueError):
        await callback.answer(
            "Commande invalide.",
            show_alert=True,
        )
        return

    telegram_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        user = await session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            await callback.answer(
                "Utilisateur non enregistré.",
                show_alert=True,
            )
            return

        order = await session.scalar(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user.id,
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
            .where(
                OrderItem.order_id == order.id
            )
            .order_by(OrderItem.id)
        )

        items = result.scalars().all()

    lines = [
        f"📦 <b>COMMANDE #{order.id}</b>",
        "",
        f"📅 {order.created_at:%d/%m/%Y %H:%M}",
        f"📌 Statut : <b>{status_label(order.status)}</b>",
        "💵 Paiement : <b>liquide sur place</b>",
        "",
    ]

    for item in items:
        lines.append(
            f"• <b>{item.product_name}</b>\n"
            f"  {item.unit_price:.2f} € × {item.quantity} = "
            f"<b>{item.subtotal:.2f} €</b>"
        )

    lines.extend([
        "",
        f"💰 <b>Total : {order.total:.2f} €</b>",
        "",
        "📍 Retrait directement en boutique.",
    ])

    await callback.answer()

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=order_detail_keyboard(
            order.status
        ),
    )


@router.message(Command("commandes"))
async def commandes_command_handler(message: Message):
    await show_orders(
        message,
        message.from_user.id,
    )
