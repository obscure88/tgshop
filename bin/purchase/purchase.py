import json

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from bin.keyboards import get_payment_keyboard, get_keyboard_for_finish
from bin.payments.payments import create_payment_form
from bin.purchase.register_purchase import register_purchase
from loader import dp
from src.const import const_ru
from bin.strings import create_comment, get_pay_message


class PurchaseCreator(StatesGroup):
    item_count = State()
    select_pay = State()
    check_purchase = State()


async def select_count(message: types.Message, item_id):
    """
    Клавиатура для выбора количества товаров

    :param message:
    :param item_id: id выброанного товара
    :return:
    """
    await PurchaseCreator.item_count.set()

    item_count = database.get_item_count(item_id)

    state = Dispatcher.get_current().current_state()
    await state.update_data(item_id=item_id)

    keyboard = types.InlineKeyboardMarkup(row_width=5)

    i = 1
    btn_list = []
    while i <= 15 and i <= item_count:
        btn_list.append(types.InlineKeyboardButton(text=f"{str(i)} шт.",
                                                   callback_data=f"select_count={str(i)}"))
        i += 1

    await state.update_data(max_count=item_count)

    keyboard.add(*btn_list)
    keyboard.add(types.InlineKeyboardButton(text="🛒 Своё значение", callback_data="user_count"))
    keyboard.add(types.InlineKeyboardButton(text=const_ru['cancel_buy'], callback_data="cancel_buy"))

    await message.answer("🛒 Введите необходимое количество товара", reply_markup=keyboard)


@dp.callback_query_handler(Regexp("select_count"), state=PurchaseCreator.item_count)
async def get_count_keyboard(call: types.CallbackQuery, state: FSMContext):
    """
    Количество товара из клавиатуры

    :param call:
    :param state:
    :return:
    """
    await call.message.delete()

    await state.update_data(count=int(call.data.split("=")[1]))
    await select_pay(call.message, state)


@dp.callback_query_handler(Regexp("user_count"), state=PurchaseCreator.item_count)
async def input_count(call: types.CallbackQuery, state: FSMContext):
    """
    Выбор количества товара для покупки

    :param call:
    :param state:
    :return:
    """
    await call.message.delete()
    data = await state.get_data()
    item_id = data['item_id']

    item_count = database.get_item_count(item_id)

    await call.message.answer("🛒 Введите количество необходимого товара:\n\n"
                              "Минимальное значение: <i>1 шт.</i>\n"
                              f"Максимальное: <i>{item_count} шт.</i>")

    await state.update_data(max_count=int(item_count))


@dp.message_handler(state=PurchaseCreator.item_count)
async def check_count(message: types.Message, state: FSMContext):
    """
    Проверка количества товара

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()

    max_count = data['max_count']
    count = message.text

    if count.isdigit() and int(count) <= max_count:
        count = int(count)
    else:
        await message.answer("❗️ Некорректное значение")
        return

    await state.update_data(count=count)
    await select_pay(message, state)


@dp.message_handler(state=PurchaseCreator.check_purchase)
async def select_pay(message: types.Message, state: FSMContext):
    """
    Выбор оплаты

    :param message:
    :param state:
    :return:
    """
    keyboard = get_payment_keyboard()
    length = len(json.loads(keyboard.as_json())["inline_keyboard"])

    if length > 0:
        keyboard.row(types.InlineKeyboardButton(text=const_ru['cancel_buy'], callback_data="cancel_buy"))
        await message.answer("💳 Выберите способ покупки", reply_markup=keyboard)
        await PurchaseCreator.next()
    else:
        await message.answer("😔 К сожалению, оплата в данный момент не работает",
                             reply_markup=get_keyboard_for_finish(message.chat.id))
        await state.finish()


@dp.callback_query_handler(Regexp("payment"), state=PurchaseCreator.select_pay)
async def payment(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    call_data = call.data.split("=")

    await state.update_data(payment=call_data[1])
    await create_purchase(call.message, state)


async def create_purchase(message: types.Message, state: FSMContext):
    """
    Обработка покупки

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    payment_type = data['payment']
    comment = create_comment()

    item_data = database.get_item(data['item_id'])
    amount = item_data[4] * int(data['count'])

    payment_form, warning_payment = create_payment_form(payment_type, amount, comment)
    message_text = get_pay_message(f"Покупка товара <b>{item_data[1]}</b>",
                                   payment_form, comment, warning_payment, amount)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text=const_ru['buy_item'], url=payment_form['link']),
                 types.InlineKeyboardButton(text=const_ru['check_buy'], callback_data="check_buy"))

    keyboard.row(types.InlineKeyboardButton(text=const_ru['cancel_buy'], callback_data="cancel_buy"))

    await message.answer(message_text, reply_markup=keyboard)
    await state.update_data(amount=amount)
    await state.update_data(comment=comment)
    await PurchaseCreator.next()


@dp.callback_query_handler(Regexp("check_buy"), state=PurchaseCreator.check_purchase)
async def check_purchase(call: types.CallbackQuery, state: FSMContext):
    """
    Проверка покупки

    :param call:
    :param state:
    :return:
    """
    data = await state.get_data()
    await register_purchase(call.message, data)


@dp.callback_query_handler(Regexp("cancel_buy"), state=PurchaseCreator)
async def cancel_buy(call: types.CallbackQuery):
    """
    Отмена покупки

    :param call:
    :return:
    """
    await call.message.delete()
    await call.message.answer("❗️ Покупка отменена")

    state = Dispatcher.get_current().current_state()
    await state.finish()
