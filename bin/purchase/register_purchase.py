from aiogram import Dispatcher, types

import database
from bin.admins import send_admins
from bin.payments.payments import check_payment
from bin.strings import get_buy_message, get_cheque_num, get_now_date
from src import config


async def register_purchase(message: types.Message, data):
    """
    Регистрация покупки

    :param message:
    :param data:
    :return:
    """
    has_payment = check_payment(data)

    item_id = data['item_id']
    amount = int(data['amount'])
    count = data['count']

    item_info = database.get_item(item_id)

    if has_payment:
        # оплата прошла успешно
        state = Dispatcher.get_current().current_state()
        await state.finish()
        await message.delete()

        items_data = database.get_item_data(item_id, count, True)

        # вся инфа о покупке
        purchase_data = dict()
        purchase_data['user_id'] = message.chat.id
        purchase_data['item_name'] = item_info[1]
        purchase_data['amount'] = amount
        purchase_data['count'] = count
        purchase_data['date'] = get_now_date()
        purchase_data['cheque'] = get_cheque_num()

        # запись покупки в БД и получение ID
        sale_id = database.add_buy(purchase_data)
        database.add_sold_item_data(sale_id, items_data)
        purchase_data['sale_id'] = sale_id

        user_text = get_buy_message(message.chat.id, purchase_data, True)
        admin_text = get_buy_message(message.chat.id, purchase_data, False)

        item_text = ""
        item_files = []

        item_size = len(items_data)
        for item in items_data:
            item_data = item[2].split("=", 2)

            if item_data[0] == "text":
                # текстовый товар
                item_text += f"{item_data[1]}\n"
            elif item_data[0] == "file":
                # файловый товар
                item_files.append(item_data[1])

        for i in range(len(item_files)):
            # отправка файловых товаров
            await message.answer_document(open(item_files[i], "rb"))

        if item_size > 10:
            config.create_folder("cheques")

            with open(f"cheques/{purchase_data['cheque']}.txt", "w") as f:
                f.write(item_text)
                f.close()

            with open(f"cheques/{purchase_data['cheque']}.txt", "rb") as f:
                await message.answer_document(document=f, caption=user_text)
                await send_admins(admin_text, document=f)
        else:
            await message.answer(user_text + item_text)
            await send_admins(admin_text + item_text)

        database.update_user(message.chat.id, message.chat.username,
                             message.chat.first_name, message.chat.last_name)
    else:
        # ошибка при оплате
        if data['payment'] == "banker":
            user = database.get_user(message.chat.id)
            user_balance = float(database.get_user_balance(user[0])) + float(amount)
            database.set_user_balance(user[0], user_balance)
            await message.answer("❗️ Ошибка при проверке оплаты\n"
                                 "Деньги были зачислены на ваш баланс\n\n"
                                 f"Текущий баланс: <b>{database.get_user_balance(user[0])} руб.</b>")
        else:
            await message.answer("❗️ Ошибка при проверке оплаты\nПроверьте еще раз")
