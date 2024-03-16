from loader import bot
from src.config import ADMIN_ID


async def send_admins(message_text, keyboard=None, document=None):
    """
    Отправка сообщений всем админам

    :param message_text: сообщение
    :param keyboard: при необходимости клавиатура
    :param document: при необходимости отправка документа
    :return:
    """
    for admin in ADMIN_ID:
        if document is not None:
            await bot.send_document(admin, document=document, caption=message_text)
        else:
            await bot.send_message(admin, message_text, reply_markup=keyboard)
