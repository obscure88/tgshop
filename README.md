# tgshop
Telegram shop for admin panel and pay

Telegram Магазинчик с широким функционалом админ-панели
Доступные платёжные системы: Yoomoney
Из способностей: рассылка, профиль юзера
Заполните settings.ini

sudo apt install python3 && python3-pip
pip3 aiogram==2.13 YooMoney
python3 main.py

Функции :
"shop": "🛒 Товары",
"profile": "📱 Профиль",
"onas": "📜 О нас",

"about_shop": "\uD83C\uDFEA Управление магазином",
"faq": "ℹ️ FAQ",
"rules": "📗 Правила",
"hello_message": "\uD83D\uDC4B Приветствие",
"comeback_message": "✋ Возвращение",

"support": "👨‍💻 Поддержка",
"my_support": "\uD83D\uDCD3 Мои обращения",
"new_support": "\uD83D\uDCCB Новое обращение",
"active_support": "\uD83D\uDCD7 Активные обращения",
"close_support": "\uD83D\uDCD5 Закрытые обращения",
"cancel_support": "\uD83D\uDEAB Отмена запроса",

"accept_rules": "✅ Ознакомлен и согласен",

"to_all_category": "⬅ Назад к категориям",
"buy": "\uD83D\uDECD Купить",
"buy_item": "\uD83D\uDCB3 Оплатить",
"check_buy": "\uD83D\uDD04 Проверка оплаты",
"cancel_buy": "\uD83D\uDEAB Отмена оплаты",

"items": "📦 Все товары магазина",
"add_item": "📓 Добавить товар",
"item_management": "📝 Управление товарами",
"edit_name": "📙 Изменить название",
"edit_desc": "📋 Изменить описание",
"edit_pic": "\uD83D\uDCF7 Изменить картинку",
"edit_price": "💵 Изменить цену",
"edit_data": "📦 Управление данными товара",
"load_data": "\uD83D\uDCD3 Дозагрузка данных",
"delete_data": "\uD83D\uDDD1 Удалить остатки",
"delete_item": "🗑 Удалить товар",

"category_management": "📁 Управление категориями",
"add_category": "📂 Добавить категорию",
"add_subcategory": "📂 Добавить подкатегорию",
"delete_category": "🗑 Удалить категорию",
"delete_subcategory": "🗑 Удалить подкатегорию",

"users": "🙍‍♂ Пользователи",
"find_user": "\uD83D\uDD0E Найти пользователя",

"statistic": "\uD83D\uDCCA Статистика",
"general": "\uD83D\uDCCA Общая",
"daily": "\uD83D\uDCC6 Ежедневная",
"all_users": "\uD83D\uDE4D\u200D♂ Все пользователи",
"all_purchases": "\uD83D\uDED2 Все покупки",

"payment": "\uD83D\uDCB3 Управление оплатой",
"qiwi": "\uD83E\uDD5D QIWI",
"yoomoney": "\uD83D\uDCB5 YooMoney",
"edit_payment": "📝 Изменить данные",
"check_payment": "🔁 Проверить кошелек",
"mailing": "\uD83D\uDCE7 Рассылки",
"create_mailing": "\uD83D\uDCEE Создать рассылку",

"edit": "\uD83D\uDCDD Редактировать",
"cancel": "Отмена",
"next": "Вперед ➡",
"back": "⬅ Назад",
"return": "◀ Вернуться",
"close": "🚫 Закрыть",
"finish": "✅ Завершить",
"yes": "✔ Да",
"no": "❌ Нет",
"delete": "🗑 Удалить",
"nothing": "😔 Ой, здесь ничего нет("

Telegram Бот требует, чтобы новый пользователь нажал на Подтвердить, чтобы быть принятым в группу/канал - это позволяет сохранять базу данных людей, которым можно сделать рассылку командой /send_all тут текст
Может приветствовать новых пользователей в чате

    Заполните данные в AutoAccept.py 11 - 14 строки
    Токен бота взять в t.me/BotFather
    Айди группы и канала можно взять через бота t.me/chatIDrobot
    Установите python с офф. сайта (поставьте галочку в начале установки Add python to path)
    Установите aiogram командой:

sudo apt install python3
pip3 install aiogram==2.22.2

Запустите командой:
python3 AutoAccept.py

AutoAccept.py​

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import Database
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import asyncio
import aiogram

bot = Bot(token="1234567890:AAKvIlbE5zo5_aq1yNe-0jgCmgSKfiMsdgDc", parse_mode='HTML')
admin_id = 123456789
group_id = -1201456669786
channelid = -10018166123577

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()

remove_keyboard_markup = types.ReplyKeyboardRemove()

class UserConfirmation(StatesGroup):
    confirmation = State()

@dp.chat_join_request_handler()
async def start1(update: types.ChatJoinRequest):
    confirm_button = KeyboardButton('Подтвердить')
    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(confirm_button)
    await bot.send_message(chat_id=admin_id, text=f"<b>➕ Новая заявка в канал: </b> @{update.from_user.username} [<code>{update.from_user.id}</code>]")
    await update.bot.send_message(chat_id=update.from_user.id, text=f'<b>‼️ {update.from_user.full_name}, для доступа к каналу нажми кнопку <u>"Подтвердить"</u></b>', reply_markup=reply_keyboard)
    state = dp.current_state(user=update.from_user.id)
    await state.set_state(UserConfirmation.confirmation)

@dp.message_handler(content_types=types.ContentType.TEXT, text=['Подтвердить'])
async def confirm_user(message: types.Message, state: FSMContext):
    await bot.approve_chat_join_request(chat_id=channelid, user_id=message.from_user.id)
    usersf = db.get_user(message.from_user.id)
    if usersf is not None:
        db.add_user(message.from_user.id)
        await bot.send_message(chat_id=admin_id, text=f"<b>✅ Приняли в канал пользователя:</b> @{message.from_user.username} [<code>{message.from_user.id}</code>]")
        await message.answer(f'<b>✅ {message.from_user.full_name} твоя <u>заявка</u> в канал была <u>прията</u>!\n\n☁️ http://commudazrdyhbullltfdy222krfjhoqzizks5ejmocpft3ijtxq5khqd.onion \n\n⚠️ Для получения актуальной ссылки в случаи блокировки, пропиши <u>/start</u></b>', disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        await state.finish()
    else:
        await message.answer(f'<b>✅ {message.from_user.full_name} твоя <u>заявка</u> в канал была <u>прията</u>!\n\n☁️ http://commudazrdyhbullltfdy222krfjhoqzizks5ejmocpft3ijtxq5khqd.onion \n\n⚠️ Для получения актуальной ссылки в случаи блокировки, пропиши <u>/start</u></b>', disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        await bot.send_message(chat_id=admin_id, text=f"<b>✅Приняли в канал пользователя:</b> @{message.from_user.username} [<code>{message.from_user.id}</code>]")
        await state.finish()


@dp.message_handler(state=UserConfirmation.confirmation)
async def handle_confirmation(message: types.Message,state=FSMContext):
    print(state)
    await message.answer('<b>⚠️ Для доступа к каналу нажми кнопку <u>"Подтвердить"</u></b>')

#######################################################

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    existing_user = db.get_user(message.from_user.id)
    if existing_user is not None:
        await message.answer("💰")
        await message.answer("<b>Привет, @{message.from_user.username}.\nhttp://commudazrdyhbullltfdy222krfjhoqzizks5ejmocpft3ijtxq5khqd.onion</b>", disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
    else:
        await message.answer("💰")
        await message.answer("<b>Привет, @{message.from_user.username}.\nhttp://commudazrdyhbullltfdy222krfjhoqzizks5ejmocpft3ijtxq5khqd.onion</b>", disable_web_page_preview=True, reply_markup=remove_keyboard_markup)
        db.add_user(message.from_user.id)

@dp.message_handler(content_types="new_chat_members")
async def on_user_join(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=admin_id, text=f'✅ Новый участник в чате:\n\n'
                                               f'{message.from_user.get_mention()} | {message.from_user.full_name}\n'
                                               f'Id: {message.from_user.id}\n'
                                               f'Username: @{message.from_user.username}\n'
                                               )
    new_msg = await message.answer(f'{message.from_user.get_mention()} добро пожаловать в чат!', disable_web_page_preview=True)
    await asyncio.sleep(15)
    try:
        await new_msg.delete()
    except Exception as e:
        pass

@dp.message_handler(content_types="left_chat_member")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="new_chat_title")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="new_chat_photo")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(content_types="delete_chat_photo")
async def on_user_join(message: types.Message):
    await message.delete()

@dp.message_handler(commands=['send_all'])
async def send_all_users(message: types.Message):
    if message.from_user.id == admin_id:
        users = db.get_users()
        successful_sends = 0
        failed_sends = 0
        for user in users:
            try:
                await bot.send_message(chat_id=user[0], text=message.text.replace("/send_all ", ""))
                await asyncio.sleep(0.5)
                successful_sends += 1
            except aiogram.utils.exceptions.TelegramAPIError as e:
                failed_sends += 1
        await bot.send_message(chat_id=admin_id, text=f"Рассылка завершена!\n\nУспешно отправлено сообщений: {successful_sends}\nСообщений с ошибками: {failed_sends}")

@dp.message_handler(content_types=['photo', 'video', 'document', 'text'], chat_id=group_id)
async def handle_comment(message: types.Message):
    if message.from_user.id != 777000:
        pass
    elif message.chat.id != group_id:
        pass
    else:
        await message.reply("+", disable_web_page_preview=True)

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        db.close()

database.py​

import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (user_id INTEGER PRIMARY KEY)''')

    def close(self):
        self.conn.close()

    def add_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
   
    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

users.db будет такая:​

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
    "user_id"    INTEGER,
    PRIMARY KEY("user_id")
);
COMMIT;


