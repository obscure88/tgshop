import asyncio
import logging

from aiogram import types

import database
from handlers import dp

logger = logging.getLogger(__name__)


async def main():
    database.open_db()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    await dp.skip_updates()
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запуск бота"),
        types.BotCommand("cancel", "Если завис бот")
    ])

    await dp.start_polling(dp)


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
