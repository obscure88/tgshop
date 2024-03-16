from bin.payments.qiwi.qiwi_params import create_qiwi_link, check_qiwi_payment
from bin.payments.yoo_money.yoo_money_params import create_yoomoney_link, check_yoomoney_payment


def create_payment_form(payment_type, amount, comment):
    """
    Создание оплаты

    :param payment_type:
    :param amount:
    :param comment:
    :return:
    """

    if payment_type == "qiwi":
        payment_form = create_qiwi_link(amount, comment)
        warning_payment = "❗️ При оплате через никнейм <b>указывайте комментарий самостоятельно и в ПЕРВОЕ ПОЛЕ</b>, " \
                          "иначе вы НЕ ПОЛУЧИТЕ ПОКУПКУ\n" \
                          "При оплате через номер телефона ничего указывать <b>не нужно</b>. Всё сделано " \
                          "автоматически ❗️\n"
    else:
        payment_form = create_yoomoney_link(amount, comment)
        warning_payment = "❗️ Для оплаты <b>необходимо перейти по ссылке, где все данные указаны автоматически</b>️\n" \
                          "Вам необходимо только нажать <b>Оплатить</b> ❗️\n"

    return payment_form, warning_payment


def check_payment(payment_data):
    amount = float(payment_data['amount'])
    payment_type = payment_data['payment']
    comment = ""

    if payment_type != "balance" and payment_type != "banker":
        comment = payment_data['comment']

    if payment_type == "qiwi":
        has_payment = check_qiwi_payment(amount, comment)
    else:
        has_payment = check_yoomoney_payment(comment)

    return has_payment
