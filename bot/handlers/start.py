from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy import select

from bot.keyboards.main import main_menu_keyboard, welcome_keyboard
from database.database import AsyncSessionLocal
from database.models import User


router = Router()


WELCOME_IMAGE = "assets/welcome.jpg"


WELCOME_TEXT = """
🛍️ Bienvenue chez Le Druide 06 !

Nous sommes ravis de vous accueillir dans notre boutique.

Découvrez nos produits et prenez le temps de parcourir notre sélection.

✨ Nous vous souhaitons une agréable visite et un excellent moment sur notre boutique !

Avant de commencer, merci de prendre connaissance et d'accepter nos conditions d'utilisation.

En cliquant sur « J'accepte », votre compte Telegram sera enregistré afin de permettre la gestion de votre panier, de vos commandes et de votre historique.
"""


MAIN_MENU_TEXT = """
🏠 MENU PRINCIPAL

Bienvenue chez Le Druide 06 ! 🛍️

Nous vous souhaitons une excellente visite.

Que souhaitez-vous faire ?
"""


@router.message(CommandStart())
async def start_handler(message: Message):
    photo = FSInputFile(WELCOME_IMAGE)

    await message.answer_photo(
        photo=photo,
        caption=WELCOME_TEXT,
        reply_markup=welcome_keyboard(),
    )


@router.callback_query(lambda callback: callback.data == "accept_terms")
async def accept_terms_handler(callback: CallbackQuery):
    user = callback.from_user

    async with AsyncSessionLocal() as session:
        existing_user = await session.scalar(
            select(User).where(User.telegram_id == user.id)
        )

        if existing_user is None:
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                accepted=True,
            )

            session.add(new_user)

        else:
            existing_user.accepted = True
            existing_user.username = user.username
            existing_user.first_name = user.first_name
            existing_user.last_name = user.last_name

        await session.commit()

    await callback.answer("Bienvenue chez Le Druide 06 !")

    await callback.message.edit_caption(
        caption=MAIN_MENU_TEXT,
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(lambda callback: callback.data == "refuse_terms")
async def refuse_terms_handler(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_caption(
        caption="""
❌ Accès refusé

Vous avez choisi de ne pas accepter les conditions.

Vous pouvez utiliser /start à tout moment pour revenir à l'accueil.
"""
    )
