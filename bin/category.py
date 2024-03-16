from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import database
from loader import dp
from src.const import is_const


class CategoryAdder(StatesGroup):
    category_name = State()


async def add_name(message: types.Message, category_id):
    """
    Добавление названий

    :param message:
    :param category_id: -1 - категория, > 0 - подкатегория (id категории)
    :return:
    """
    await message.answer("✏️ Введите название категории\n<b>Одна категория - одна строка</b>")
    await CategoryAdder.category_name.set()

    state = Dispatcher.get_current().current_state()
    await state.update_data(category_id=category_id)


@dp.message_handler(state=CategoryAdder.category_name)
async def add_to_db(message: types.Message, state: FSMContext):
    """
    Запись категорий в БД

    :param state:
    :param message:
    :return:
    """
    data = await state.get_data()
    await state.finish()
    category_id = int(data["category_id"])

    categories = message.text.split("\n")
    for i in range(len(categories)):
        if is_const(categories[i]):
            categories.pop(i)

    if category_id == -1:
        # добавление категории
        database.add_categories(categories)
    else:
        # добавление подкатегории
        database.add_subcategories(categories, category_id)

    await message.answer(f"✅ Всего категорий добавлено: {len(categories)}")
