import asyncio
import json

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import CantParseEntities

import database
from bin.keyboards import cancel_keyboard, get_keyboard_for_finish
from loader import bot, dp
from src import config
from src.const import is_const, const_ru


class MailingCreator(StatesGroup):
    text = State()
    check = State()
    send = State()


async def new_mailing(message: types.Message):
    """
    Запрос текста рассылки

    :param message:
    :return:
    """
    await message.answer(f"✏️ Введите текст вашей рассылки. Присутствует поддержка форматирования\n"
                         "<b>Вы так же можете прикрепить фото, и указать текст в описании к картинке</b>\n"
                         "<b>Или переслать необходимое сообщение</b>",
                         reply_markup=cancel_keyboard)
    await MailingCreator.text.set()


@dp.message_handler(state=MailingCreator.text, content_types=['text', 'photo'])
async def mailing_text(message: types.Message, state: FSMContext):
    """
    Получение текста для рассылки

    :param message:
    :param state:
    :return:
    """
    photo = ""

    if len(message.photo) > 0:
        # рассылка с фотографией
        text = message.html_text
        photo = message.photo[-1].file_id
    else:
        text = message.html_text
    await state.update_data(mailing_text=text)
    await state.update_data(mailing_photo=photo)

    await MailingCreator.next()
    await mailing_check(message, state)


@dp.message_handler(state=MailingCreator.check)
async def mailing_check(message: types.Message, state: FSMContext):
    """
    Проверка рассылки на корректность

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()

    message_text = "Проверьте рассылку на корректность перед отправкой\n" \
                   f"Если все верно, нажмите <b>✅ Отправить</b>\n" \
                   f"Или нажмите <b>{const_ru['edit']}</b>\n\n" \
                   f"{data['mailing_text']}"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="✅ Отправить", callback_data="send_mailing"),
                 types.InlineKeyboardButton(text=const_ru['edit'], callback_data="edit_mailing"))

    try:
        if data['mailing_photo'] != "":
            await message.answer_photo(photo=data['mailing_photo'],
                                       caption=message_text,
                                       reply_markup=keyboard)
        else:
            await message.answer(message_text, reply_markup=keyboard)

        await MailingCreator.next()
    except CantParseEntities:
        await message.answer("❗️ Ошибка в форматировании ❗️\n\nВведите текст <b>еще раз</b>")
        await state.finish()
        await new_mailing(message)
        return


@dp.callback_query_handler(Regexp("edit_mailing"), state=MailingCreator.send)
async def edit_mailing(call: types.CallbackQuery, state: FSMContext):
    """
    Редактирование рассыки

    :param call:
    :param state:
    :return:
    """
    await call.message.delete()
    await state.finish()
    await new_mailing(call.message)


@dp.callback_query_handler(Regexp("send_mailing"), state=MailingCreator.send)
async def send_mailing(call: types.CallbackQuery):
    """
    Отправка рассылки

    :param call:
    :return:
    """
    await call.message.delete()

    state = Dispatcher.get_current().current_state()
    data = await state.get_data()
    user_list = database.get_all_users()

    text = data['mailing_text']
    if is_const(text):
        await message.answer("❗️ Некорректный текст рассылки ❗️\n\nВведите текст <b>еще раз</b>")
        await state.finish()
        await new_mailing(message)
        return

    photo = data['mailing_photo']
    await state.finish()

    success = 0
    bad = 0
    await call.message.answer("✅ Рассылка началась",
                              reply_markup=get_keyboard_for_finish(call.message.chat.id))

    if photo != "":
        # рассылка с фото
        for user in user_list:
            try:
                await bot.send_photo(user[0], photo=photo, caption=text)
                success += 1
            except Exception:
                bad += 1

            await asyncio.sleep(0.05)
    else:
        # рассылка текста
        for user in user_list:
            try:
                await bot.send_message(user[0], text)
                success += 1
            except Exception:
                bad += 1

            await asyncio.sleep(0.05)

    await call.message.answer(f"✅ Рассылка завершена\nВсего отправлено: <b>{len(user_list)} шт.</b>")
    await call.message.answer(f"✅ Успешно: <b>{success} шт.</b>\n❌ Не отправлено: <b>{bad} шт.</b>")

