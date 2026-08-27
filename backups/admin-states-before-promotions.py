from aiogram.fsm.state import State, StatesGroup


class ProductStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_stock = State()
    waiting_category = State()

    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_stock = State()


class CategoryStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_sort_order = State()

    editing_name = State()
    editing_description = State()
    editing_sort_order = State()


class InformationStates(StatesGroup):
    waiting_field = State()
