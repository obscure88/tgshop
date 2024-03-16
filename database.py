import sqlite3

from src.config import DIR
from bin.strings import get_now_date

DATABASE = f"{DIR}/shopDB.sqlite"


def connect_db():
    """
    Создание подключения к БД
    :return:
    """
    return sqlite3.connect(DATABASE)


def open_db():
    """
    Проверка и создание таблиц в БД при первом запуске
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        # Пользователи
        cur.execute("CREATE TABLE IF NOT EXISTS UserList ("
                    "user_id INT,"
                    "username TEXT,"
                    "firstName TEXT,"
                    "lastName TEXT,"
                    "balance REAL,"
                    "inviting INT,"
                    "regDate TEXT)")

        # Обращения в поддержку
        cur.execute("CREATE TABLE IF NOT EXISTS Support ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "user_id INT,"
                    "message TEXT,"
                    "type INT,"
                    "state INT,"
                    "answer TEXT,"
                    "date TEXT,"
                    "FOREIGN KEY (user_id) references UserList(user_id),"
                    "FOREIGN KEY (type) references SupportTypes(id))")

        # Типы обращений
        cur.execute("CREATE TABLE IF NOT EXISTS SupportTypes ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name TEXT)")

        # Запись типов обращений
        if len(cur.execute("SELECT * FROM SupportTypes").fetchall()) == 0:
            types = [("❓ Вопрос",), ("💳 Оплата",), ("📚 Товары",), ("📝 Прочее",)]
            cur.executemany("INSERT INTO SupportTypes (name) VALUES (?)", types)

        # Лист с товарами
        cur.execute("CREATE TABLE IF NOT EXISTS ItemList ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name TEXT, "
                    "desc TEXT, "
                    "pic TEXT, "
                    "price INT, "
                    "category INT, "
                    "subcategory INT, "
                    "FOREIGN KEY (category) references Category(id), "
                    "FOREIGN KEY (subcategory) references Subcategory(id))")

        # Данные товаров
        cur.execute("CREATE TABLE IF NOT EXISTS Items ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "item_id INT, "
                    "data TEXT, "
                    "FOREIGN KEY (item_id) references ItemList(id) )")

        # Категории
        cur.execute("CREATE TABLE IF NOT EXISTS Category ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name TEXT)")

        # Подкатегории
        cur.execute("CREATE TABLE IF NOT EXISTS Subcategory ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name TEXT, "
                    "category_id INT, "
                    "FOREIGN KEY (category_id) references Category(id))")

        # Покупки
        cur.execute("CREATE TABLE IF NOT EXISTS Sales ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "user_id INT, "
                    "item_name TEXT, "
                    "amount INT, "
                    "count INT, "
                    "date TEXT, "
                    "cheque TEXT, "
                    "FOREIGN KEY (user_id) references UserList(user_id))")

        # Приобретенные аккаунты
        cur.execute("CREATE TABLE IF NOT EXISTS SoldItems ("
                    "sale_id INT,"
                    "item_data TEXT,"
                    "FOREIGN KEY (sale_id) references Sales(id))")

        # QIWI
        cur.execute("CREATE TABLE IF NOT EXISTS Qiwi ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "num TEXT,"
                    "token TEXT,"
                    "nickname TEXT)")

        if len(cur.execute("SELECT * FROM Qiwi").fetchall()) == 0:
            cur.execute("INSERT INTO Qiwi (num, token, nickname) VALUES (?, ?, ?)",
                        ("num", "token", "nickname"))

        # YooMoney
        cur.execute("CREATE TABLE IF NOT EXISTS YooMoney ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "num TEXT,"
                    "token TEXT)")

        if len(cur.execute("SELECT * FROM YooMoney").fetchall()) == 0:
            cur.execute("INSERT INTO YooMoney (num, token) VALUES (?, ?)",
                        ("num", "token"))

        # BTC Banker
        cur.execute("CREATE TABLE IF NOT EXISTS Banker ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "api_id INT,"
                    "api_hash TEXT)")

        if len(cur.execute("SELECT * FROM Banker").fetchall()) == 0:
            cur.execute("INSERT INTO Banker (api_id, api_hash) VALUES (?, ?)",
                        (0, "token"))

        # Прочие параметры
        cur.execute("CREATE TABLE IF NOT EXISTS Params ("
                    "key TEXT,"
                    "value TEXT)")

        if len(cur.execute("SELECT * FROM Params").fetchall()) == 0:
            param_list = [
                ("faq", "📋 Здесь может быть FAQ для вашего магазина\n\n<i>Разработано Боженькой</i>"),
                ("rules", "📗 Здесь могут быть правила для вашего магазина\n\n<i>Разработано Боженькой</i>"),
                ("hello_message", "Добро пожаловать, @{username}"),
                ("comeback_message", "С возвращением, @{username}"),
                ("qiwi_payment", "number")
            ]

            cur.executemany("INSERT INTO Params (key, value) VALUES (?, ?)", param_list)


# Запросы к БД

# # # Пользователи # # #

def add_user(user_id, username, first_name, last_name, inviting):
    """
    Добавление пользоватея

    :param user_id: id юзера
    :param username: ник пользователя
    :param first_name:
    :param last_name:
    :param inviting: id пригласившего пользователя
    :return: true - юзер добавлен, false - юзер уже существует
    """
    with connect_db() as db:
        cur = db.cursor()

        user = cur.execute("SELECT * FROM UserList WHERE user_id = ?", [user_id]).fetchall()

        if len(user) == 0:
            cur.execute("INSERT INTO UserList (user_id, username, "
                        "firstName, lastName, balance, inviting, regDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [user_id, username, first_name, last_name, 0, inviting, get_now_date()])
            return True
        else:
            update_user(user_id, username, first_name, last_name)
            return False


def get_user(user):
    """
    Получение пользователя

    :param user:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        if str(user).startswith("@"):
            return cur.execute("SELECT * FROM UserList WHERE username = ?", [user.split("@")[1]]).fetchone()
        else:
            return cur.execute("SELECT * FROM UserList WHERE user_id = ?", [user]).fetchone()


def get_daily_users(date):
    """
    Получение новых пользователей за день

    :param date: дата
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute(f"SELECT * FROM UserList WHERE regDate LIKE '%{date}%'").fetchall()


def update_user(user_id, username, first_name, last_name):
    """
    Обновление данных о пользователе

    :param user_id:
    :param username:
    :param first_name:
    :param last_name:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET username = ?, firstName = ?, lastName = ?"
                    " WHERE user_id = ?", [username, first_name, last_name, user_id])


def set_user_balance(user_id, amount):
    """
    Пополнение баланса

    :param user_id: id пользователя
    :param amount: сумма пополнения
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET balance = ? WHERE user_id = ?", [amount, user_id])


def get_user_balance(user):
    """
    Получение баланса пользователя

    :param user: id пользователя
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM UserList WHERE user_id = ?", [user]).fetchone()[4]


def get_all_users():
    """
    Все пользователи магазина

    :return: список всех пользователей
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM UserList").fetchall()


# # # Покупка товара # # #

def add_buy(purchase_data):
    """
    Запись новой покупки

    :param purchase_data: данные о покупке
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Sales (user_id, item_name, amount, count, date, cheque) VALUES (?, ?, ?, ?, ?, ?)",
                    (purchase_data['user_id'], purchase_data['item_name'], purchase_data['amount'],
                     purchase_data['count'], purchase_data['date'], purchase_data['cheque']))

        return cur.execute("SELECT * FROM Sales WHERE cheque = ?", [purchase_data['cheque']]).fetchone()[0]


def add_sold_item_data(sale_id, item_data):
    """
    Добавление данных о проданном товаре

    :param sale_id: id продажи
    :param item_data: данные товара
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        for item in item_data:
            cur.execute("INSERT INTO SoldItems (sale_id, item_data) VALUES (?, ?)", (sale_id, item[2]))


def old_sold_buy(sale_id, item_data):
    """
    Добавление старой покупки

    :param sale_id: id продажи
    :param item_data: данные товара
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        cur.execute("INSERT INTO SoldItems (sale_id, item_data) VALUES (?, ?)",
                    (sale_id, item_data))


def get_user_buy(user_id):
    """
    Получение всех покупок пользователя

    :param user_id: id пользователя
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Sales WHERE user_id = ?", [user_id]).fetchall()


def get_all_sales():
    """
    Получение всех покупок в магазине

    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Sales").fetchall()


def get_daily_sales(date):
    """
    Получение покупок за день

    :param date: дата
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute(f"SELECT * FROM Sales WHERE date LIKE '%{date}%'").fetchall()


# # # Категории # # #

def get_categories():
    """
    Получение всех категорий
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Category").fetchall()


def get_category(category_id):
    """
    Получение категории по id

    :param category_id: id категории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Category WHERE id = ?", [category_id]).fetchone()


def get_subcategories(category_id):
    """
    Получение подкатегорий из категории

    :param category_id: id категории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Subcategory WHERE category_id = ?", [category_id]).fetchall()


def get_all_subcategories():
    """
    Получение подкатегорий

    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Subcategory").fetchall()


def add_categories(category_list):
    """
    Добавление категорий

    :param category_list: список категорий
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        for category in category_list:
            cur.execute("INSERT INTO Category (name) VALUES (?)", [category])


def add_category(category):
    """
    Добавление категории

    :param category:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Category (name) VALUES (?)", [category])


def add_subcategories(category_list, category_id):
    """
    Добавление подкатегорий

    :param category_list: названия категорий
    :param category_id: id главной категории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        for category in category_list:
            cur.execute("INSERT INTO Subcategory (name, category_id) VALUES (?, ?)",
                        (category, category_id))


def add_subcategory(category_name, category_id):
    """
    Добавление подкатегории

    :param category_name:
    :param category_id:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Subcategory (name, category_id) VALUES (?, ?)",
                    (category_name, category_id))


def delete_category(category_id):
    """
    Удаление категории

    :param category_id: id категории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM ItemList WHERE category = ?", [category_id])
        cur.execute("DELETE FROM Subcategory WHERE category_id = ?", [category_id])
        cur.execute("DELETE FROM Category WHERE id = ?", [category_id])


def delete_subcategory(subcategory_id):
    """
    Удаление подкатегории

    :param subcategory_id: id подкатегории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM ItemList WHERE subcategory = ?", [subcategory_id])
        cur.execute("DELETE FROM Subcategory WHERE id = ?", [subcategory_id])


# # # Товары # # #

def get_items_category(category_id, subcategory_id):
    """
    Получение товаров из категории или подкатегории

    :param category_id: id категории
    :param subcategory_id: id подкатегории
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM ItemList WHERE category = ? AND subcategory = ?",
                           [category_id, subcategory_id]).fetchall()


def get_item(item_id):
    """
    Получение товара по id

    :param item_id: id товара
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM ItemList WHERE id = ?", [item_id]).fetchone()


def get_item_count(item_id):
    """
    Получение количества доступных товаров

    :param item_id: id товара
    :return: количество свободных товаров
    """
    with connect_db() as db:
        cur = db.cursor()
        return len(cur.execute("SELECT * FROM Items WHERE item_id = ?", [item_id]).fetchall())


def add_item(item):
    """
    Добавление товара

    :param item: данные о товаре в JSON формате
    :return: созданный товар
    """
    with connect_db() as db:
        cur = db.cursor()

        cur.execute("INSERT INTO ItemList (name, desc, pic, price, category, subcategory) VALUES (?, ?, ?, ?, ?, ?)",
                    (item["name"], item["desc"], item["pic"],
                     item["price"], item["category"], item["subcategory"]))

        return cur.execute("SELECT * FROM ItemList WHERE name = ?", [item["name"]]).fetchone()


def delete_item(item_id):
    """
    Удаление товара

    :param item_id: id товара
    :return:
    """
    delete_all_item_data(item_id)

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM ItemList WHERE id = ?", [item_id])


# # # Позиции товара # # #

def add_item_data(item, item_data):
    """
    Добавление данных для товара

    :param item: данные о товаре в JSON формате
    :param item_data: данные товара
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Items (item_id, data) VALUES (?, ?)",
                    (item["id"], item_data))


def get_all_item_data(item_id):
    """
    Получение всех данных товара

    :param item_id:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()

        return cur.execute("SELECT * FROM Items WHERE item_id = ?", [item_id]).fetchall()


def get_item_data(item_id, count, if_delete):
    """
    Получение данных товара в определенном количестве

    :param item_id: id товара
    :param count: количество
    :param if_delete: true - после получения удалить данные
    :return:
    """

    with connect_db() as db:
        cur = db.cursor()

        item_list = cur.execute("SELECT * FROM Items WHERE item_id = ?", [item_id]).fetchmany(count)

        if if_delete:
            # удаление товаров из БД
            for item in item_list:
                cur.execute("DELETE FROM Items WHERE id = ?", [item[0]])

    return item_list


def get_data(data_id):
    """
    Позиция по id

    :param data_id: id позиции
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Items WHERE id = ?", [data_id]).fetchone()


def update_item_data(data_id, new_data):
    """
    Обновление позиции по id

    :param data_id: id позиции
    :param new_data: новые данные позиции
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Items SET data = ? WHERE id = ?", [new_data, data_id])


def delete_all_item_data(item_id):
    """
    Удаление всех данных товара

    :param item_id: id товара
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM Items WHERE item_id = ?", [item_id])


def delete_item_data(data_id):
    """
    Удаление позиции товара

    :param data_id: id позиции
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM Items WHERE id = ?", [data_id])


# # # Параметры товара # # #

def edit_item_param(item_id, param_name, param_value):
    """
    Изменение значения товара

    :param item_id: id товара
    :param param_name: название параметра
    :param param_value: значение
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute(f"UPDATE ItemList SET {param_name} = ? WHERE id = ?", (param_value, item_id))

# # # Оплата # # #

def get_qiwi():
    """
    Получение Qiwi кошелька

    :return: данные кошелька
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Qiwi").fetchone()


def edit_qiwi(qiwi_data):
    """
    Запись данных о Qiwi кошельке

    :param qiwi_data: данные о кошельке в json
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Qiwi SET num = ? , token = ? , nickname = ? WHERE id = ?",
                    (qiwi_data['num'], qiwi_data['token'], qiwi_data['nickname'], 1))


def get_yoomoney():
    """
    Получение данных о YooMoney

    :return: данные yoomoney
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM YooMoney").fetchone()


def edit_yoomoney(yoomoney_data: dict):
    """
    Запись данных о YooMoney кошельке

    :param yoomoney_data: данные о кошельке в json
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE YooMoney SET num = ? , token = ? WHERE id = ?",
                    (yoomoney_data['num'], yoomoney_data['token'], 1))


def get_banker():
    """
    Получение данных о Banker

    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Banker").fetchone()


def edit_banker(banker_data: dict):
    """
    Запись данных о приложении

    :param banker_data:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Banker SET api_id = ? , api_hash = ? WHERE id = ?",
                    (banker_data['api_id'], banker_data['api_hash'], 1))


# # # Поддержка # # #

def get_support_types():
    """
    Получение всех типов запросов

    :return: массив со всеми типами запросов
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM SupportTypes").fetchall()


def get_support_type(id):
    """
    Получение типа запроса по id

    :param id: id запроса
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM SupportTypes WHERE id = ?", [id]).fetchone()


def register_support(data):
    """
    Регистрация обращения

    :param data: данные об обращении в JSON
    :return: id обращения
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Support (user_id,  message, type, state, answer, date) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (data['user_id'], data['message'], data['type'], 0, "", get_now_date()))

        return cur.execute("SELECT * FROM Support WHERE user_id = ? AND message = ? AND type = ?",
                           (data['user_id'], data['message'], data['type'])).fetchone()[0]


def get_supports(state):
    """
    Получение обращений с определенным состоянием

    :param state: состояние: 0 - активно, 1 - закрыто
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Support WHERE state = ?", [state]).fetchall()


def get_user_supports(user_id):
    """
    Получение всех запросов пользователя

    :param user_id:
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Support WHERE user_id = ?", [user_id]).fetchall()


def get_support(id):
    """
    Получение запроса

    :param id: id запроса
    :return: данные о запросе
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Support WHERE id = ?", [id]).fetchone()


def close_support(id, data):
    """
    Закрытие запроса

    :param id: id запроса
    :param data: данные запроса
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Support SET state = ?, answer = ? WHERE id = ?",
                    (1, data['answer'], id))


def delete_support(id):
    """
    Удаление запроса

    :param id: id запроса
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM Support WHERE id = ?", [id])


# # # Прочее # # #

def get_param(key):
    """
    Получение параметра по ключу

    :param key: ключ
    :return: значение ключа
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Params WHERE key = ?", [key]).fetchone()[1]


def set_param(key, value):
    """
    Замена значения по ключу

    :param key: ключ
    :param value: значение
    :return:
    """
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Params SET value = ? WHERE key = ?", (value, key))
