import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.commands import set_bot_commands

from bot.handlers import (
    admin_router,
    cart_router,
    menu_router,
    orders_router,
    shop_router,
    start_router,
)

from config import BOT_TOKEN
from database.database import Base, engine

from database.models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    User,
    Information,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def init_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def main():
    await init_database()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)
    dispatcher.include_router(shop_router)
    dispatcher.include_router(cart_router)
    dispatcher.include_router(menu_router)
    dispatcher.include_router(orders_router)
    dispatcher.include_router(admin_router)

    # Commandes visibles dans le menu Telegram
    await set_bot_commands(bot)

    logging.info("Commandes Telegram configurées.")
    logging.info("Bot démarré.")

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
