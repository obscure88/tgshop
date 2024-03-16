import collections

from aiogram import types
from aiogram.dispatcher.filters import IDFilter

import database
from bin import keyboards
from bin.users import user_finder
from bin.keyboards import create_list_keyboard
from bin.mailing import new_mailing
from bin.statisctic import get_sort_sales_keyboard
from bin.strings import format_stat, get_user_link
from loader import dp
from src.config import ADMIN_ID
from src.const import *


# # # Управление товарами и категориями # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["items"])
async def item_management(message: types.Message):
    """
    Управление товарами

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru["item_management"], const_ru["category_management"])
    keyboard.row(const_ru["back"])

    await message.answer(message.text, reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["category_management"])
async def category_management(message: types.Message):
    """
    Управление категориями

    :param message:
    :return:
    """
    keyboard = keyboards.create_category_keyboard("edit_category")

    keyboard.row(types.InlineKeyboardButton(text=const_ru["add_category"],
                                            callback_data="add_category=-1"))

    keyboard.add(keyboards.CLOSE_BTN)

    await message.answer("📂 Все доступные категории", reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["item_management"])
async def item_management(message: types.Message):
    """
    Управление товарами

    :param message:
    :return:
    """
    keyboard = keyboards.create_category_keyboard("get_item_category")
    keyboard.add(keyboards.CLOSE_BTN)
    await message.answer(const_ru["item_management"], reply_markup=keyboard)


# # # О магазине # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['about_shop'])
async def about_shop(message: types.Message):
    """
    Сведения о магазине

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru["items"], const_ru["payment"])
    keyboard.row(const_ru["faq"], const_ru["rules"])
    keyboard.row(const_ru["hello_message"], const_ru["comeback_message"])
    keyboard.row(const_ru["back"])
    await message.answer(const_ru['about_shop'], reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['hello_message'])
async def hello_message(message: types.Message):
    """
    Приветствие

    :param message:
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=const_ru["edit"], callback_data="edit_hello"))

    hello = database.get_param('hello_message').format(username=message.chat.username)
    message_text = f"📋 Пример сообщения\n\n{hello}"

    await message.answer(message_text, reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['comeback_message'])
async def comeback_message(message: types.Message):
    """
    Приветствие

    :param message:
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=const_ru["edit"], callback_data="edit_comeback"))

    hello = database.get_param('comeback_message').format(username=message.chat.username)
    message_text = f"📋 Пример сообщения\n\n{hello}"

    await message.answer(message_text, reply_markup=keyboard)


# # # Рассылки # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['mailing'])
async def mailing(message: types.Message):
    """
    Меню создания рассылки

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru['create_mailing'])
    keyboard.row(const_ru["back"])
    await message.answer(const_ru['mailing'], reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['create_mailing'])
async def create_mailing(message: types.Message):
    """
    Создание рассылки

    :param message:
    :return:
    """
    await new_mailing(message)


# # # Оплата # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["payment"])
async def payment_edit(message: types.Message):
    """
    Управление оплатой

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru["qiwi"], const_ru["yoomoney"])
    keyboard.row(const_ru["back"])
    await message.answer(message.text, reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["qiwi"])
async def qiwi_edit(message: types.Message):
    """
    Управление QIWI

    :param message:
    :return:
    """
    qiwi_type = database.get_param("qiwi_payment")

    if qiwi_type == "number":
        qiwi = "Номер телефона"
        change = "Никнейм"
        change_param = "nickname"
    else:
        qiwi = "Никнейм"
        change = "Номер телефона"
        change_param = "number"

    message_text = f"{const_ru['qiwi']}\n" \
                   "📱 Текущий способ оплаты: \n<i>{qiwi_type}</i>"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=const_ru["edit_payment"],
                                            callback_data="edit_qiwi"))
    keyboard.add(types.InlineKeyboardButton(text=const_ru["check_payment"],
                                            callback_data="check_qiwi"))

    if database.get_qiwi()[3] != "None":
        keyboard.add(types.InlineKeyboardButton(text=f"🔁 Поменять на: {change}",
                                                callback_data=f"change_qiwi={change_param}"))
    keyboard.add(keyboards.CLOSE_BTN)

    await message.answer(message_text.format(qiwi_type=qiwi), reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["yoomoney"])
async def yoomoney_edit(message: types.Message):
    """
    Управление YooMoney

    :param message:
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=const_ru["edit_payment"],
                                            callback_data="edit_yoomoney"))
    keyboard.add(types.InlineKeyboardButton(text=const_ru["check_payment"],
                                            callback_data="check_yoomoney"))
    keyboard.add(keyboards.CLOSE_BTN)

    await message.answer(message.text, reply_markup=keyboard)


# # # Статистика # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["statistic"])
async def statistics(message: types.Message):
    """
    Статистика

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru["general"], const_ru["daily"])
    keyboard.row(const_ru["back"])

    await message.answer(const_ru["statistic"], reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["general"])
async def general(message: types.Message):
    """
    Общая статистика

    :param message:
    :return:
    """
    all_users = database.get_all_users()

    message_text = f"🏪 Статистика магазина\n" \
                   f"🙍‍♂ Количество участников: <b>{len(all_users)} чел.</b>\n"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text=const_ru['all_users'], callback_data="all_users_stat"),
                 types.InlineKeyboardButton(text=const_ru['all_purchases'], callback_data="all_purchases_stat"))
    keyboard.add(keyboards.CLOSE_BTN)
    await message.answer(message_text, reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["daily"])
async def daily(message: types.Message):
    """
    Ежедневная статистика

    :param message:
    :return:
    """
    await message.answer(const_ru["daily"], reply_markup=get_sort_sales_keyboard(0))


# # # Пользователи # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["users"])
async def users(message: types.Message):
    """
    Пользователи магазина

    :param message:
    :return:
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru['find_user'])
    keyboard.row(const_ru['back'])
    await message.answer(const_ru["users"], reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru['find_user'])
async def find_user(message: types.Message):
    """
    Поиск пользователя

    :param message:
    :return:
    """
    await user_finder.get_user_id(message)

# # # Поддержка # # #

@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["active_support"])
async def active_support(message: types.Message):
    """
    Все активные обращения

    :param message:
    :return:
    """
    keyboard = create_list_keyboard(data=database.get_supports(0),
                                    last_index=0,
                                    page_click=f"get_supports=0",
                                    btn_text_param="support",
                                    btn_click="get_support")
    await message.answer(const_ru["active_support"], reply_markup=keyboard)


@dp.message_handler(IDFilter(chat_id=ADMIN_ID), regexp=const_ru["close_support"])
async def closed_support(message: types.Message):
    """
    Все закрытые обращения

    :param message:
    :return:
    """
    keyboard = create_list_keyboard(data=database.get_supports(1),
                                    last_index=0,
                                    page_click=f"get_supports=1",
                                    btn_text_param="support",
                                    btn_click="get_support")
    await message.answer(const_ru["close_support"], reply_markup=keyboard)
