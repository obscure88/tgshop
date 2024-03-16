from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import dp
from bin.payments.yoo_money.yoo_money_params import yoomoney_auth, generate_token
from src.const import is_const
from bin.keyboards import cancel_keyboard, get_keyboard_for_finish


class YooMoneyEditor(StatesGroup):
    client_id = State()
    redirect_uri = State()
    authorize = State()


async def client_id(message: types.Message):
    """
    Запрос client_id

    :param message:
    :return:
    """
    await message.answer("Зарегестрируйте API <a href='https://yoomoney.ru/myservices/new'>здесь</a>\n"
                         "📱 Введите <b>client_id</b>", reply_markup=cancel_keyboard)
    await YooMoneyEditor.client_id.set()


@dp.message_handler(state=YooMoneyEditor.client_id)
async def redirect_uri(message: types.Message, state: FSMContext):
    """
    Запрос redirect_uri

    :param message:
    :param state:
    :return:
    """
    id = message.text
    if is_const(id):
        await message.answer("❗️ Введите корректный <b>client_id</b>")
        return

    await state.update_data(client_id=id)
    await YooMoneyEditor.next()
    await message.answer("🌐 Введите <b>redirect_uri</b>")


@dp.message_handler(state=YooMoneyEditor.redirect_uri)
async def authorize_url(message: types.Message, state: FSMContext):
    """
    Авторизация кошелька

    :param message:
    :param state:
    :return:
    """
    uri = message.text
    if is_const(uri):
        await message.answer("❗️ Введите корректный <b>redirect_uri</b>")
        return

    await state.update_data(redirect_uri=uri)
    data = await state.get_data()

    auth_url = yoomoney_auth(data['client_id'], uri)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="💻 Активация", url=auth_url))

    await message.answer("❗️ Перейдите по ссылке, подтвердите данные и скопируйте полученную ссылку после "
                         "переадресации\n "
                         "❗️ Время действия полученной ссылки <b>1 минута</b>",
                         reply_markup=keyboard)
    await YooMoneyEditor.next()


@dp.message_handler(state=YooMoneyEditor.authorize)
async def authorize_payment(message: types.Message, state: FSMContext):
    """
    Разбор ссылки после переадресации и получение токена

    :param message:
    :param state:
    :return:
    """
    url = message.text
    if is_const(url):
        await message.answer("❗️ Некорректная ссылка")
        return

    data = await state.get_data()

    access_token = generate_token(data['client_id'], data['redirect_uri'], url)

    if access_token is not None:
        # токен получен успешно
        num = access_token.split(".")[0]
        await state.update_data(num=num)
        await state.update_data(token=access_token)

        yoomoney_data = await state.get_data()
        database.edit_yoomoney(yoomoney_data)

        message_text = "✅ Кошелек изменен"
    else:
        message_text = "❗️ Кошелек не доступен, повторите добавление снова"

    await message.answer(message_text, reply_markup=get_keyboard_for_finish(message.chat.id))

    await state.finish()
