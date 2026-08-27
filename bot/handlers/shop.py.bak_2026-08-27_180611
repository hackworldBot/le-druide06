from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy import select

from bot.keyboards.shop import (
    categories_keyboard,
    product_keyboard,
    products_keyboard,
)
from database.database import AsyncSessionLocal
from database.models import Category, Product


router = Router()


@router.callback_query(lambda callback: callback.data == "menu_shop")
async def shop_handler(callback: CallbackQuery):
    await callback.answer()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.sort_order, Category.name)
        )

        categories = result.scalars().all()

    if not categories:
        await callback.message.edit_text(
            """
🛍️ BOUTIQUE

La boutique ne contient actuellement aucune catégorie.

Revenez plus tard.
""",
            reply_markup=__import__(
                "bot.keyboards.common",
                fromlist=["back_to_menu_keyboard"],
            ).back_to_menu_keyboard(),
        )
        return

    await callback.message.edit_text(
        """
🛍️ BOUTIQUE

Choisissez une catégorie :
""",
        reply_markup=categories_keyboard(categories),
    )


@router.callback_query(lambda callback: callback.data.startswith("category:"))
async def category_handler(callback: CallbackQuery):
    await callback.answer()

    category_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        category = await session.get(Category, category_id)

        if category is None or not category.is_active:
            await callback.message.edit_text(
                "❌ Cette catégorie n'existe plus.",
            )
            return

        result = await session.execute(
            select(Product)
            .where(
                Product.category_id == category_id,
                Product.is_active.is_(True),
            )
            .order_by(Product.name)
        )

        products = result.scalars().all()

    if not products:
        await callback.message.edit_text(
            f"""
📂 {category.name}

Aucun produit disponible dans cette catégorie.
""",
            reply_markup=products_keyboard([]),
        )
        return

    text = f"📂 <b>{category.name}</b>\n\n"

    if category.description:
        text += f"{category.description}\n\n"

    text += "Choisissez un produit :"

    await callback.message.edit_text(
        text,
        reply_markup=products_keyboard(products),
    )


@router.callback_query(lambda callback: callback.data.startswith("product:"))
async def product_handler(callback: CallbackQuery):
    await callback.answer()

    product_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)

        if product is None or not product.is_active:
            await callback.message.edit_text(
                "❌ Ce produit n'est plus disponible."
            )
            return

        category_id = product.category_id

    stock_text = (
        f"📊 Stock : {product.stock}"
        if product.stock > 0
        else "❌ Rupture de stock"
    )

    text = f"""
📦 {product.name}

"""

    if product.description:
        text += f"{product.description}\n\n"

    text += f"""
💰 Prix : {product.price:.2f} €
{stock_text}
"""

    keyboard = product_keyboard(product.id, category_id)

    if product.stock <= 0:
        keyboard.inline_keyboard[0][0].text = "❌ Rupture de stock"
        keyboard.inline_keyboard[0][0].callback_data = "out_of_stock"

    if product.image:
        try:
            await callback.message.delete()

            await callback.message.answer_photo(
                photo=product.image,
                caption=text,
                reply_markup=keyboard,
            )
            return

        except Exception:
            pass

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
    )


@router.callback_query(lambda callback: callback.data == "out_of_stock")
async def out_of_stock_handler(callback: CallbackQuery):
    await callback.answer(
        "❌ Ce produit est actuellement en rupture de stock.",
        show_alert=True,
    )
