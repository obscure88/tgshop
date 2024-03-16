import json

from aiogram import types
from aiogram.dispatcher.filters import Regexp

import database
from handlers.message.user_message import shop_message
from loader import dp
from bin.purchase.purchase import select_count
from bin import keyboards
from src.const import const_ru
from bin.keyboards import create_list_keyboard

# # # Товары # # #

@dp.callback_query_handler(Regexp("all_category"))
async def all_category(call: types.CallbackQuery):
    """
    Вызов метода shop_message() из user_message

    :param call:
    :return:
    """
    await call.message.delete()
    await shop_message(call.message)


@dp.callback_query_handler(Regexp("select_category"))
async def select_category(call: types.CallbackQuery):
    """
    Вывод товаров и подкатегорий в выбранной категории

    :param call:
    :return:
    """
    await call.message.delete()

    data = call.data.split("=")
    keyboard = keyboards.create_category_items_keyboard(data[1], "select_subcategory", "select_item")
    length = len(json.loads(keyboard.as_json())["inline_keyboard"])

    message_text = "🛒 Все доступные товары и подкатегории"
    if length == 0:
        message_text = const_ru["nothing"]

    keyboard.add(types.InlineKeyboardButton(text=const_ru["back"],
                                            callback_data="all_category"))
    keyboard.add(keyboards.CLOSE_BTN)
    await call.message.answer(message_text, reply_markup=keyboard)


@dp.callback_query_handler(Regexp("select_subcategory"))
async def select_subcategory(call: types.CallbackQuery):
    """
    Все товары в выбранной подкатегории

    :param call:
    :return:
    """
    await call.message.delete()

    data = call.data.split("=")[1].split("|")
    keyboard = keyboards.create_subcategory_items_keyboard(data[0], data[1], "select_item")
    length = len(json.loads(keyboard.as_json())["inline_keyboard"])

    message_text = "🛒 Все доступные товары"
    if length == 0:
        message_text = const_ru["nothing"]

    keyboard.row(types.InlineKeyboardButton(text=const_ru["back"],
                                            callback_data=f"select_category={data[0]}"),
                 types.InlineKeyboardButton(text=const_ru["to_all_category"],
                                            callback_data="all_category"))
    keyboard.add(keyboards.CLOSE_BTN)

    await call.message.answer(message_text, reply_markup=keyboard)


@dp.callback_query_handler(Regexp("select_item"))
async def select_item(call: types.CallbackQuery):
    """
    Информация о выбранном предмете

    :param call:
    :return:
    """
    await call.message.delete()
    data = call.data.split("=")

    item = database.get_item(data[1])
    item_count = database.get_item_count(data[1])

    message_text = f"📓 Название: <b>{item[1]}</b>\n" \
                   f"📋 Описание:\n{item[2]}\n" \
                   f"💳 Цена: {item[4]} руб.\n\n" \
                   f"📦 Доступно к покупке: <i>{item_count} шт.</i>"

    keyboard = types.InlineKeyboardMarkup()

    if item_count > 0:
        keyboard.add(types.InlineKeyboardButton(text=const_ru["buy"],
                                                callback_data=f"buy_item={data[1]}"))
    else:
        message_text += "\n\n <b>❗️ ️ Товар временно отсутствует️️</b>"

    if item[6] == 0:
        back_callback = f"select_category={item[5]}"
    else:
        back_callback = f"select_subcategory={item[5]}|{item[6]}"

    keyboard.row(types.InlineKeyboardButton(text=const_ru["back"],
                                            callback_data=back_callback),
                 types.InlineKeyboardButton(text=const_ru["to_all_category"],
                                            callback_data="all_category"))

    keyboard.add(keyboards.CLOSE_BTN)
    if item[3] != "":
        await call.message.answer_photo(open(item[3], "rb"), message_text, reply_markup=keyboard)
    else:
        await call.message.answer(message_text, reply_markup=keyboard)


@dp.callback_query_handler(Regexp("buy_item"))
async def buy_item(call: types.CallbackQuery):
    """
    Обработка покупки товара

    :param call:
    :return:
    """
    await call.message.delete()
    data = call.data.split("=")

    await select_count(call.message, data[1])


# # # Обращения # # #

@dp.callback_query_handler(Regexp("get_user_supports"))
async def get_user_supports(call: types.CallbackQuery):
    """
    Получение запросов пользователя

    :param call:
    :return:
    """
    await call.message.delete()
    call_data = call.data.split("=")
    data = call_data[1].split("|")
    keyboard = create_list_keyboard(data=database.get_user_supports(data[0]),
                                    last_index=int(data[1]),
                                    page_click=f"get_user_supports={data[0]}",
                                    btn_text_param="user_support",
                                    btn_click="get_user_support")

    await call.message.answer(const_ru["get_supports"], reply_markup=keyboard)


@dp.callback_query_handler(Regexp("get_user_support"))
async def get_support(call: types.CallbackQuery):
    """
    Просмотр запроса пользоватея

    :param call:
    :return:
    """
    await call.message.delete()
    call_data = call.data.split("=")
    support_data = database.get_support(call_data[1])

    keyboard = types.InlineKeyboardMarkup()

    if int(support_data[5]) == 0:
        support_state = "✅ Активно"
    else:
        support_state = "❌ Закрыто\n" \
                        "➖➖➖➖➖➖➖➖➖➖\n" \
                        f"📧 Ответ:\n\n" \
                        f"{support_data[6]}"

    message_text = f"🆔 Номер запроса: <b>{call_data[1]}</b>\n" \
                   "➖➖➖➖➖➖➖➖➖➖\n" \
                   f"📗 Тема запроса: <b>{database.get_support_type(support_data[4])[1]}</b>\n" \
                   f"📋 Описание:\n{support_data[3]}\n" \
                   "➖➖➖➖➖➖➖➖➖➖\n" \
                   f"📱 Состояние: {support_state}"

    keyboard.add(keyboards.CLOSE_BTN)
    await call.message.answer(message_text, reply_markup=keyboard)
