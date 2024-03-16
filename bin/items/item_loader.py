from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from handlers.message.other_message import back_message
from loader import dp
from src import config
from src.const import const_ru


class ItemLoader(StatesGroup):
    item_data = State()


async def add_data(message: types.Message, item_id, additional=False):
    """
    Проверка цены товара
    Запрос данных товара

    :param message:
    :param item_id: id товара
    :param additional: дозагрузка товара, по умолчанию False
    :return:
    """
    item_name = database.get_item(item_id)[1]

    message_text = "📦 Введите данные товара\n\n" \
                   "<b>Примеры загрузки:</b>\n\n" \
                   "<i>Товар 1</i>\n" \
                   "<i>Товар 2</i>\n" \
                   "<i>Товар n</i>\n\n" \
                   "<i>Сгруппированные документы</i>\n\n" \
                   f"Товары будут загружаться до тех пор, пока вы не нажмете <b>{const_ru['finish']}</b>"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(const_ru["finish"])

    await message.answer(message_text, reply_markup=keyboard)
    await ItemLoader.item_data.set()

    state = Dispatcher.get_current().current_state()
    await state.update_data(id=item_id)
    await state.update_data(name=item_name)
    await state.update_data(additional=additional)


@dp.message_handler(state=ItemLoader.item_data, content_types=['document', 'text'])
async def add_to_db(message: types.Message, state: FSMContext):
    """
    Проверка данных товара
    Запись товара в БД

    :param message:
    :param state:
    :return:
    """
    item = await state.get_data()

    if message.text == const_ru["finish"]:
        await finish_loading(message)
        return

    if message.document is not None:
        # Загрузка товара как документ
        src = "items"
        config.create_folder(src)

        src += f"/{item['id']}"
        config.create_folder(src)

        document = message.document
        src += f"/{document['file_name']}"
        await message.document.download(destination=src)

        database.add_item_data(item, f"file={src}")
    else:
        # Загрузка товара как тест
        item_data = message.text.split("\n")

        for i in range(len(item_data)):
            database.add_item_data(item, f"text={item_data[i]}")

    await message.answer(f"✅ Товар загружен")


async def finish_loading(message: types.Message):
    """
    Завершение загрузки товаров

    :param message:
    :return:
    """
    state = Dispatcher.get_current().current_state()
    item_data = await state.get_data()
    await state.finish()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if item_data['additional']:
        keyboard.row(const_ru["item_management"], const_ru["category_management"])
        keyboard.row(const_ru["back"])

    await message.answer(f"✅ Загрузка <b>{item_data['name']} завершена</b>", reply_markup=keyboard)

    if item_data['additional']:
        from bin.items.item_editor import edit_item_menu

        await edit_item_menu(message, item_data['id'])
    else:
        await back_message(message)
