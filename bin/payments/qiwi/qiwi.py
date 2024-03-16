from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import dp
from bin.payments.qiwi.qiwi_params import check_qiwi, get_nickname
from src.const import is_const
from bin.keyboards import cancel_keyboard, get_keyboard_for_finish


class QiwiEditor(StatesGroup):
    num = State()
    token = State()


async def qiwi_num(message: types.Message):
    """
    Запрос номера Qiwi

    :param message:
    :return:
    """
    await message.answer("📱 Введите номер телефона <b>без +</b>", reply_markup=cancel_keyboard)
    await QiwiEditor.num.set()


@dp.message_handler(state=QiwiEditor.num)
async def qiwi_token(message: types.Message, state: FSMContext):
    """
    Запрос токена

    :param message:
    :param state:
    :return:
    """
    if not message.text.isdigit():
        await message.answer("❗️ Введите корректный номер ❗️")
        return

    await state.update_data(num=message.text)
    await QiwiEditor.next()
    await message.answer("📟 Введите токен Qiwi")


@dp.message_handler(state=QiwiEditor.token)
async def check_token(message: types.Message, state: FSMContext):
    """
    Проверка токена

    :param message:
    :param state:
    :return:
    """
    token = message.text
    if is_const(token):
        await message.answer("❗️ Введите корректный токен ❗️")
        return

    data = await state.get_data()

    if check_qiwi(data['num'], token):
        await message.answer("✅ Кошелек активен")
        await state.update_data(token=token)

        await check_nickname(message, state)

    else:
        await message.answer("❗️ Кошелек не доступен, повторите добавление снова ❗️")
        await state.finish()
        return


async def check_nickname(message: types.Message, state: FSMContext):
    """
    Запрос никнейма из Qiwi
    Запись кошелька в БД

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()

    response_data = get_nickname(data['num'], data['token'])
    await message.answer(f"🏧 Ваш никнейм кошелька: <b>{response_data['nickname']}</b>")
    await state.update_data(nickname=str(response_data['nickname']))

    data = await state.get_data()
    await state.finish()

    database.edit_qiwi(data)
    await message.answer("✅ Кошелек изменен", reply_markup=get_keyboard_for_finish(message.chat.id))
