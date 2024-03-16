from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from bin import keyboards
from bin.keyboards import get_keyboard_for_finish, cancel_keyboard
from bin.users.user_info import get_user_info
from loader import dp
from src.const import is_const


class UserFinder(StatesGroup):
    get_user = State()


async def get_user_id(message: types.Message):
    """
    Поиск пользователя по нику или id

    :param message:
    :return:
    """
    await message.answer("📝 Введите ID пользователя или ник через @", reply_markup=cancel_keyboard)
    await UserFinder.get_user.set()


@dp.message_handler(state=UserFinder.get_user)
async def user_info(message: types.Message, state: FSMContext):
    """
    Информация о пользователе

    :param message:
    :param state:
    :return:
    """
    username = message.text

    user = get_user_info(username)

    if user == "❗️ Пользователь не найден":
        keyboard = get_keyboard_for_finish(message.chat.id)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(keyboards.CLOSE_BTN)

    await state.finish()
    await message.answer(user, reply_markup=keyboard)
