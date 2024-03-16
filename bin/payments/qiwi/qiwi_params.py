from requests import Session

import database
from src.const import const_ru


def create_qiwi_link(amount, comment):
    """
    Создание ссылки на оплату

    :param amount: сумма для оплаты
    :param comment: комментарий
    :return:
    """
    qiwi_data = database.get_qiwi()

    payment_form = dict()
    payment_form['name'] = const_ru["qiwi"]

    payment_type = database.get_param("qiwi_payment")

    if payment_type == "number":
        # оплата по номеру
        payment_form["link"] = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={qiwi_data[1]}&" \
                               f"amountInteger={amount}&amountFraction=0&extra%5B%27comment%27%5D={comment}&" \
                               f"currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        payment_form["key"] = "Номер"
        payment_form["value"] = qiwi_data[1]
    elif payment_type == "nickname":
        # оплата по нику
        payment_form["link"] = f"https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D={qiwi_data[3]}&" \
                      f"amountInteger={amount}&amountFraction=0&currency=643&blocked[0]=account&" \
                      f"extra%5B%27accountType%27%5D=nickname"

        payment_form["key"] = "Никнейм"
        payment_form["value"] = qiwi_data[3]

    return payment_form


def check_qiwi_payment(amount, comment):
    """
    Проверка оплаты

    :param amount: сумма оплаты
    :param comment: комментарий
    :return: true - оплата прошла, false - оплаты нет
    """
    request = Session()

    qiwi_data = database.get_qiwi()

    request.headers["authorization"] = f"Bearer {qiwi_data[2]}"
    params_get = {"rows": 5, "operation": "IN"}
    response = request.get(
        f"https://edge.qiwi.com/payment-history/v2/persons/{qiwi_data[1]}/payments",
        params=params_get)

    last_payments: list = response.json()["data"]

    for i in range(len(last_payments)):
        comment_pay = str(last_payments[i]["comment"])
        amount_pay = float(last_payments[i]["sum"]["amount"])
        currency_pay = str(last_payments[i]["sum"]["currency"])

        if comment == comment_pay and amount_pay == amount and currency_pay == "643":
            return True

    return False


def check_db_qiwi():
    """
    Проверка Qiwi из БД

    :return: true - доступен, false - нет
    """
    qiwi_data = database.get_qiwi()

    return check_qiwi(qiwi_data[1], qiwi_data[2])


def check_qiwi(num, token):
    """
    Проверка Qiwi кошелька на доступность

    :param num: номер
    :param token: токен
    :return: true - токен активен, false - токен не активен, или ошибка на сервере
    """
    request = Session()
    request.headers["authorization"] = f"Bearer {token}"
    param = {"rows": 5, "operation": "IN"}
    response = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{num}/payments",
                           params=param)

    return response.status_code == 200


def get_nickname(num, token):
    """
    Получение никнейма кошелька

    :param num: номер
    :param token: токен
    :return: никнейм кошелька
    """
    request = Session()
    request.headers["authorization"] = f"Bearer {token}"
    response = request.get(f"https://edge.qiwi.com/qw-nicknames/v1/persons/{num}/nickname")

    return response.json()
