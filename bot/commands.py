from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Démarrer le bot",
        ),
        BotCommand(
            command="boutique",
            description="Ouvrir la boutique",
        ),
        BotCommand(
            command="panier",
            description="Voir mon panier",
        ),
        BotCommand(
            command="commandes",
            description="Voir mes commandes",
        ),
        BotCommand(
            command="admin",
            description="Administration des commandes",
        ),
    ]

    await bot.set_my_commands(commands)
