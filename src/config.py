import configparser
import os

DIR = os.path.abspath(__file__)[:-14]

config = configparser.ConfigParser()
config.read(f"{DIR}/settings.ini")
TOKEN = config["settings"]["token"]
COMMENT = config["settings"]["comment_pay"]
get_id = config["settings"]["admin_id"]
ADMIN_ID = []

if "," in get_id:
    get_id = get_id.split(",")
    for a in get_id:
        ADMIN_ID.append(str(a))
else:
    try:
        ADMIN_ID = [str(get_id)]
    except ValueError:
        ADMIN_ID = [0]
        print("Не указан Admin_ID")


def is_admin(user_id):
    """
    Проверка юзера на админа

    :param user_id: id юзера
    :return: true - юзер админ, false - нет
    """
    return str(user_id) in ADMIN_ID


def create_folder(src):
    """
    Проверка/создание папки с путём src

    :param src: путь к папке
    :return:
    """
    if not os.path.exists(src):
        os.mkdir(src)
