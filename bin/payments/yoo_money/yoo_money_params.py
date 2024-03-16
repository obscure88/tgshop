import requests
from requests import Session, post
from yoomoney import Quickpay, Client

import database
from src.const import const_ru


def create_yoomoney_link(amount, comment):
    """
    Генерация ссылки на оплату
    
    :param amount: стоимость
    :param comment: комментарий
    :return:
    """
    yoomoney_data = database.get_yoomoney()

    payment_form = dict()
    payment_form["name"] = const_ru["yoomoney"]

    quick_pay = Quickpay(
        receiver=yoomoney_data[1],
        quickpay_form="shop",
        targets="Пополнение баланса",
        paymentType="SB",
        sum=amount,
        label=comment
    )

    payment_form["link"] = quick_pay.base_url
    payment_form["key"] = "Номер"
    payment_form["value"] = yoomoney_data[1]

    return payment_form


def check_yoomoney_payment(comment):
    """
    Проверка оплаты

    :param comment: комментарий
    :return: true - оплата прошла, false - оплаты нет
    """
    yoomoney_data = database.get_yoomoney()
    client = Client(yoomoney_data[2])
    history = client.operation_history(label=comment)

    for operation in history.operations:
        comment_payment = str(operation.label)

        if comment_payment == comment:
            return True

    return False


def check_db_yoomoney():
    """
    Проверка YooMoney из БД

    :return: true - доступен, false - нет
    """
    yoomoney_data = database.get_yoomoney()

    return check_yoomoney(yoomoney_data[2])


def check_yoomoney(token):
    """
    Проверка YooMoney на доступность

    :param token: токен кошелька
    :return: true - токен активен, false - токен не активен, или ошибка на сервере
    """
    request = Session()
    request.headers["Authorization"] = "Bearer " + token

    try:
        response = request.get("http://yoomoney.ru/api/account-info")

        return response.status_code == 200
    except requests.exceptions.ReadTimeout:
        return False


def yoomoney_auth(client_id, redirect_uri):
    """
    Авторизация кошелька YooMoney

    :param client_id: client_id приложения
    :param redirect_uri: url для переадресации
    :return: ссылка для получения токена авторизации
    """
    data = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'account-info operation-history operation-details'
    }

    response = post("http://yoomoney.ru/oauth/authorize", params=data)

    return response.url


def generate_token(client_id, redirect_uri, url):
    """
    Генерация токена из полученной ссылки

    :param client_id: client_id приложения
    :param redirect_uri: url для переадресации
    :param url: ссылка после переадресации
    :return: токен кошелька, None в случае ошибки
    """
    url_split = url.split("?")
    auth_code = url_split[1].split("=")[1]

    auth = {
        'code': auth_code,
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }

    response = post("http://yoomoney.ru/oauth/token", params=auth)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None
