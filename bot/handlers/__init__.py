from bot.handlers.admin import router as admin_router
from bot.handlers.cart import router as cart_router
from bot.handlers.menu import router as menu_router
from bot.handlers.orders import router as orders_router
from bot.handlers.shop import router as shop_router
from bot.handlers.start import router as start_router

__all__ = [
    "start_router",
    "menu_router",
    "shop_router",
    "cart_router",
    "orders_router",
    "admin_router",
]
