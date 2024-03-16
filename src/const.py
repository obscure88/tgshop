import json

from src.config import DIR

json_file = open(f"{DIR}/src/const.json", encoding='utf-8')
const_file = json.loads(json_file.read())

const_ru: dict = const_file["ru"]

def is_const(word):
    """
    Проверка слова на константу
    :param word: слово
    :return: true - константа, false - нет
    """
    for value in const_ru.values():
        if word == value:
            return True

    return False
