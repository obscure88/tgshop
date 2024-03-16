from aiogram.dispatcher.filters.state import StatesGroup, State


class BotStates(StatesGroup):
    new_user = State()
