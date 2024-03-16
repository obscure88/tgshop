from loader import dp
from src import config
from bin.keyboards import *


@dp.message_handler(regexp=const_ru["back"])
async def back_message(message: types.Message):
    """
    Главное меню

    :param message:
    :return:
    """
    if config.is_admin(message.chat.id):
        keyboard = admin_keyboard
    else:
        keyboard = user_keyboard

    await message.answer("🔹 Главное меню 🔹", reply_markup=keyboard)


@dp.message_handler()
async def other_message(message: types.Message):
    """
    Обработка всех прочих сообщений

    :param message:
    :return:
    """
    if config.is_admin(message.chat.id):
        keyboard = admin_keyboard
    else:
        keyboard = user_keyboard

    await message.answer("😔 Не могу разобрать текст", reply_markup=keyboard)
