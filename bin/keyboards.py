import os

from bin.payments.qiwi.qiwi_params import check_db_qiwi
from bin.payments.yoo_money.yoo_money_params import check_db_yoomoney
from src.config import is_admin
from bin.strings import *
from aiogram import types

user_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_keyboard.row(const_ru["shop"])
user_keyboard.row(const_ru["profile"], const_ru["onas"])

admin_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.row(const_ru["shop"], const_ru["profile"])
admin_keyboard.row(const_ru["about_shop"])
admin_keyboard.row(const_ru["support"])
admin_keyboard.row(const_ru["statistic"], const_ru["users"], const_ru["mailing"])

CLOSE_BTN = types.InlineKeyboardButton(text=const_ru["close"], callback_data="close")

cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.row(const_ru['cancel'])


def get_keyboard_for_finish(user_id):
    """
    Получение клавиатуры после завершения действия

    :param user_id: user id
    :return:
    """
    if is_admin(user_id):
        return admin_keyboard
    else:
        return user_keyboard


def create_category_keyboard(method):
    """
    Создание клавиатуры с категориями

    :param method: метод для callback_data
    :return:
    """
    categories = database.get_categories()

    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(categories)):
        keyboard.add(types.InlineKeyboardButton(
            text=categories[i][1],
            callback_data=f"{method}={categories[i][0]}"
        ))

    return keyboard


def create_subcategory_keyboard(category_id, method):
    """
    Создание клавиатуры с подкатегориями

    :param category_id: id категории
    :param method: метод для callback_data
    :return:
    """
    subcategories = database.get_subcategories(category_id)

    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(subcategories)):
        keyboard.add(types.InlineKeyboardButton(
            text=subcategories[i][1],
            callback_data=f"{method}={subcategories[i][0]}"
        ))

    return keyboard


def create_category_items_keyboard(category_id, method_subcategory, method_item):
    """
    Создание клавиатуры с подкатегориями и товарами в категории

    :param category_id: id категории
    :param method_subcategory: метод категории для callback_data
    :param method_item: метод товара для callback_data
    :return:
    """

    subcategories = database.get_subcategories(category_id)

    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(subcategories)):
        keyboard.add(types.InlineKeyboardButton(
            text=subcategories[i][1],
            callback_data=f"{method_subcategory}={category_id}|{subcategories[i][0]}"
        ))

    items = database.get_items_category(category_id, 0)
    for i in range(len(items)):
        keyboard.add(types.InlineKeyboardButton(
            text=item_format(items[i]),
            callback_data=f"{method_item}={items[i][0]}"
        ))

    return keyboard


def create_subcategory_items_keyboard(category_id, subcategory_id, method_item):
    """
    Создание клавиатуры с товарами в подкатегории

    :param category_id: id категории
    :param subcategory_id: id подкатегории
    :param method_item: метод товара для callback_data
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()

    items = database.get_items_category(category_id, subcategory_id)
    for i in range(len(items)):
        keyboard.add(types.InlineKeyboardButton(
            text=item_format(items[i]),
            callback_data=f"{method_item}={items[i][0]}"
        ))

    return keyboard


def get_payment_keyboard():
    """
    Клавиатура с доступными способами оплаты
    :return:
    """

    keyboard = types.InlineKeyboardMarkup()

    if check_db_qiwi():
        keyboard.add(types.InlineKeyboardButton(text=const_ru["qiwi"],
                                                callback_data="payment=qiwi"))

    if check_db_yoomoney():
        keyboard.add(types.InlineKeyboardButton(text=const_ru["yoomoney"],
                                                callback_data="payment=yoomoney"))

    return keyboard


def create_list_keyboard(data, last_index, page_click: str, btn_text_param, btn_click, back_method=None):
    """
    Создание страничной клавиатуры

    :param data: данные для клавиатуры
    :param last_index: послендий индекс
    :param page_click: метод для нажатия вперед/назад
    :param btn_text_param: текст для кнопки
    :param btn_click: метод для кнопки
    :param back_method: метод для кнопки назад, по умолчанию None
    :return:
    """
    keyboard = types.InlineKeyboardMarkup()
    btn_list = []

    btn_text = ""

    if page_click.endswith("="):
        callback = f"{page_click}"
    else:
        callback = f"{page_click}|"

    if last_index >= 10:
        btn_list.append(types.InlineKeyboardButton(
            text=const_ru['back'], callback_data=f"{callback}{(last_index - 10)}"
        ))

    if len(data) > 0:
        limit = last_index + 10

        while last_index < limit and last_index < len(data):
            click = f"{btn_click}={data[last_index][0]}"

            if btn_text_param == "support":
                btn_text = f"#{data[last_index][0]} | {data[last_index][1]}"
            elif btn_text_param == "user_support":
                btn_text = f"#{data[last_index][0]}"
            elif btn_text_param == "item_data":
                btn_text = f"{data[last_index][2].split('=')[1]}"
            elif btn_text_param == "daily_stat":
                btn_text = f"{data[last_index]}"
                click = f"{btn_click}={data[last_index]}|0"
            elif btn_text_param == "daily_purchases":
                click = f"{btn_click}={data[last_index]}|{(limit - 10)}"

            keyboard.add(
                types.InlineKeyboardButton(text=btn_text,
                                           callback_data=click)
            )
            last_index += 1

        if last_index < len(data):
            btn_list.append(types.InlineKeyboardButton(
                text=const_ru['next'], callback_data=f"{callback}{last_index}"
            ))

        keyboard.row(*btn_list)

    if back_method is not None:
        keyboard.add(types.InlineKeyboardButton(text=const_ru["back"],
                                                callback_data=back_method))
    keyboard.add(CLOSE_BTN)

    return keyboard
