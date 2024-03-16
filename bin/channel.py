from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import dp
from src.const import is_const


class ChannelEditor(StatesGroup):
    param_value = State()


async def input_channel_value(message: types.Message, param_key):
    """
    Введение нового значения

    :param message:
    :param param_key: ключ параметра
    :return:
    """
    await ChannelEditor.param_value.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(key=param_key)

    message_text = "✏️ Введите ID канала"

    await message.answer(message_text)


@dp.message_handler(state=ChannelEditor.param_value)
async def add_to_db(message: types.Message, state: FSMContext):
    """
    Проверка значения и запись в БД

    :param message:
    :param state:
    :return:
    """
    value = message.text

    if is_const(value) or not message.text.lstrip("-").isdigit():
        await message.answer("❗️ Некорректное значение")
        return

    data = await state.get_data()
    await state.finish()

    database.set_param(data['key'], value)
    await message.answer("✅ Значение изменено")
