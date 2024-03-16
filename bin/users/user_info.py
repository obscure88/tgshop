import database
from bin.strings import get_user_link


def get_user_info(username):
    """
    Получение информации о пользователе

    :param username: юзернейм или id пользователя
    :return:
    """
    user = database.get_user(username)

    if user is None:
        return "❗️ Пользователь не найден"

    sales_list = database.get_user_buy(user[0])
    user_info = f"🙍‍♂ Пользователь: {get_user_link(username)}\n" \
                f"🆔 ID: <b>{user[0]}</b>\n" \
                f"➖➖➖➖➖➖➖➖➖➖\n" \
                f"🛒 Количество покупок: <b>{len(sales_list)} шт.</b>\n" \
                f"💰 Общая сумма: <b>{sum(row[3] for row in sales_list)} руб.</b>\n" \
                f"➖➖➖➖➖➖➖➖➖➖\n" \
                f"📱 Последние 10 покупок:\n\n"

    sales_list = sales_list[::-1][:10]

    for sale in sales_list:
        user_info += f"▫ {sale[2]} | {sale[4]} шт. | {sale[3]} руб. | {sale[6]}\n"

    return user_info
