from aiogram import types
from aiogram.dispatcher.filters import Regexp

from loader import dp

@dp.callback_query_handler(Regexp("close"))
async def close_callback(call: types.CallbackQuery):
    """
    Удаление текущего сообщения

    :param call:
    :return:
    """
    await call.message.delete()
