from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import bot, dp
from bin.admins import send_admins
from src.const import is_const
from bin.strings import get_user_link


class AdminSupport(StatesGroup):
    support_answer = State()


async def get_answer(message: types.Message, support_id):
    """
    Запрос ответа на запрос

    :param message:
    :param support_id: id запроса
    :return:
    """
    await message.answer("📕 Напишите ответ")
    await AdminSupport.support_answer.set()
    state = Dispatcher.get_current().current_state()
    await state.update_data(support_id=support_id)


@dp.message_handler(state=AdminSupport.support_answer)
async def send_answer(message: types.Message, state: FSMContext):
    """
    Отправка ответа

    :param message:
    :param state:
    :return:
    """
    answer = message.text
    if is_const(answer):
        await message.answer("❗️ Некорректное значение")
        return

    data = await state.get_data()
    data['answer'] = answer

    support_data = database.get_support(data['support_id'])
    database.close_support(data['support_id'], data)

    user_message = "✅ Ваш запрос рассмотрен\n" \
                   "➖➖➖➖➖➖➖➖➖➖\n" \
                   f"🆔 Номер запроса: <b>{data['support_id']}</b>\n" \
                   f"📕 Ответ:\n\n{answer}"

    await bot.send_message(support_data[1], user_message)

    admin_message = "✅ Ответ отправлен\n" \
                    "➖➖➖➖➖➖➖➖➖➖\n" \
                    f"🙍‍♂ Ответил: {get_user_link(message.chat.id)}\n" \
                    "➖➖➖➖➖➖➖➖➖➖\n" \
                    f"🆔 Номер запроса: <b>{data['support_id']}</b>\n" \
                    f"🙍‍♂ Пользователь: <b>@{get_user_link(support_data[1])}</b>\n" \
                    f"📋 Описание:\n{support_data[2]}\n" \
                    "➖➖➖➖➖➖➖➖➖➖\n" \
                    f"📕 Ответ:\n{answer}"

    await send_admins(admin_message)
    await state.finish()
