from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import dp
from bin.admins import send_admins
from src.const import const_ru, is_const
from bin.strings import get_user_link


class UserSupport(StatesGroup):
    support_type = State()
    support_message = State()


async def select_type(message: types.Message):
    """
    Выбор типа обращения

    :param message:
    :return:
    """
    await UserSupport.support_type.set()

    support_list = database.get_support_types()
    keyboard = types.InlineKeyboardMarkup()

    for i in range(len(support_list)):
        keyboard.add(types.InlineKeyboardButton(text=support_list[i][1],
                                                callback_data=f"support_type={support_list[i][0]}"))
    keyboard.add(types.InlineKeyboardButton(text=const_ru["cancel_support"],
                                            callback_data="cancel_support"))

    await message.answer("👨‍💻 Выберите тему запроса", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("support_type"), state=UserSupport.support_type)
async def input_message(call: types.CallbackQuery):
    """
    Запрос сообщения

    :param call:
    :return:
    """
    await call.message.delete()
    call_data = call.data.split("=")

    state = Dispatcher.get_current().current_state()
    await state.update_data(user_id=call.message.chat.id)
    await state.update_data(username=call.message.chat.username)
    await state.update_data(type=call_data[1])
    await UserSupport.next()

    await call.message.answer("📋 Опишите вашу проблему/вопрос")


@dp.message_handler(state=UserSupport.support_message)
async def send_support(message: types.Message, state: FSMContext):
    """
    Отправка запроса

    :param message:
    :param state:
    :return:
    """
    message_text = message.html_text
    if is_const(message.text):
        await message.answer("❗️ Некорректное значение")
        return

    await state.update_data(message=message_text)
    data = await state.get_data()
    await state.finish()

    support_id = database.register_support(data)

    user_message = "✔️ Ваш запрос отправлен\n\n" \
                   f"🆔 Номер запроса: {support_id}"

    admin_message = "👨‍💻 Новый запрос\n" \
                    "➖➖➖➖➖➖➖➖➖➖\n" \
                    f"🆔 Номер запроса: <b>{support_id}</b>\n" \
                    f"🙍‍♂ Пользователь: {get_user_link(message.chat.id)}\n" \
                    "➖➖➖➖➖➖➖➖➖➖\n" \
                    f"📗 Тема запроса: <b>{database.get_support_type(data['type'])[1]}</b>\n" \
                    f"📋 Описание:\n\n{data['message']}"

    await message.answer(user_message)
    await send_admins(admin_message)

    await state.finish()


@dp.callback_query_handler(Regexp("cancel_support"), state=UserSupport)
async def cancel_support(call: types.CallbackQuery):
    """
    Отмена обращения

    :param call:
    :return:
    """
    await call.message.delete()
    state = Dispatcher.get_current().current_state()
    await call.message.answer("❗️ Обращение отменено")
    await state.finish()
