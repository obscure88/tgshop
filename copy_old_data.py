# Скрипт для переноса данных
# Инструкция по запуску находится в файле "Перенос данных со старой версии"
import os
import sqlite3
import sys
import time
from datetime import datetime

import database
from source.payments.qiwi.qiwi_params import get_nickname


class Database:
    def __init__(self):
        self.old = "shop.sqlite"
        self.new = "shopDB.sqlite"

    def open_old(self):
        return sqlite3.connect(self.old)

    def open_new(self):
        return sqlite3.connect(self.new)

    def copy_users(self):
        """
        Перенос пользователей

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()
            user_list = cur.execute("SELECT * FROM UserList").fetchall()

        print(f"Перенесено 0/{len(user_list)}")
        for i in range(len(user_list)):
            database.add_user(user_list[i][0])

            if i % 50 == 0:
                print(f"Перенесено {i}/{len(user_list)}")

    def copy_payment(self):
        """
        Перенос кошельков

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()

            qiwi_data = cur.execute("SELECT * FROM Qiwi").fetchone()
            # yoomoney_data = cur.execute("SELECT * FROM YooMoney").fetchone()

        # киви
        qiwi = dict()
        qiwi['num'] = qiwi_data[0]
        qiwi['token'] = qiwi_data[1]
        qiwi['nickname'] = get_nickname(qiwi_data[0], qiwi_data[1])
        database.edit_qiwi(qiwi)

        # yoomoney
        # yoo_money = dict()
        # yoo_money['num'] = yoomoney_data[0]
        # yoo_money['token'] = yoomoney_data[1]
        # database.edit_yoomoney(yoo_money)

    def copy_faq(self):
        """
        Перенос FAQ

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()
            old_faq = cur.execute("SELECT * FROM Faq").fetchone()

        database.set_param("faq", old_faq[0])

    def copy_categories(self):
        """
        Перенос категорий

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()
            categories = cur.execute("SELECT * FROM Category").fetchall()

        for category in categories:
            database.add_category(category[1])
            print(f"[INFO] Категория {category[1]} перенесена")

    def copy_subcategories(self):
        """
        Копирование подкатегорий

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()
            categories = cur.execute("SELECT * FROM Category").fetchall()
            subcategories = cur.execute("SELECT * FROM SubCategory").fetchall()

        id = 1
        for i in range(len(categories)):
            for subcategory in subcategories:
                if int(subcategory[2]) == categories[i][0]:
                    database.add_subcategory(subcategory[1], id)
                    print(f"[INFO] Подкатегория {subcategory[1]} перенесена")
            id += 1

    def copy_items(self):
        """
        Копирование всех товаров

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()

            old_categories = cur.execute("SELECT * FROM Category").fetchall()
            old_subcategories = cur.execute("SELECT * FROM SubCategory").fetchall()

            new_subcategories = database.get_all_subcategories()

            category_id = 1
            for category in old_categories:
                # сортировка товаров без подкатегории
                item_list = cur.execute("SELECT * FROM ItemsCount WHERE category = ? AND subcategory = ?",
                                        (category[0], "")).fetchall()
                for item in item_list:
                    new_item = dict()
                    new_item['name'] = item[1]
                    new_item['desc'] = item[2]
                    new_item['pic'] = ""
                    new_item['price'] = item[3]
                    new_item['category'] = category_id
                    new_item['subcategory'] = 0

                    new_item['id'] = database.add_item(new_item)[0]

                    item_data = cur.execute("SELECT * FROM Items WHERE name = ? AND category = ?",
                                            (item[1], category[0])).fetchall()

                    for data in item_data:
                        data_text: str = data[6]

                        if data_text.startswith("[file]="):
                            data_text = f"file={data[6].split('[file]=')[1]}"
                        else:
                            data_text = f"text={data[6]}"

                        database.add_item_data(new_item, data_text)

                    print(f"[INFO] Товар '{item[1]}' перенесен")

                category_id += 1

            category_id = 1
            for category in old_categories:
                for i in range(len(old_subcategories)):
                    # сортировка товаров с подкатегориями
                    item_list = cur.execute("SELECT * FROM ItemsCount WHERE category = ? AND subcategory = ?",
                                            (category[0], old_subcategories[i][0])).fetchall()
                    for item in item_list:
                        new_item = dict()
                        new_item['name'] = item[1]
                        new_item['desc'] = item[2]
                        new_item['pic'] = ""
                        new_item['price'] = item[3]
                        new_item['category'] = category_id
                        new_item['subcategory'] = new_subcategories[i][0]

                        new_item['id'] = database.add_item(new_item)[0]

                        item_data = cur.execute(
                            "SELECT * FROM Items WHERE name = ? AND category = ? AND subcategory = ?",
                            (item[1], category[0], new_subcategories[i][0])).fetchall()

                        for data in item_data:
                            data_text: str = data[6]

                            if data_text.startswith("[file]="):
                                data_text = f"file={data[6].split('[file]=')[1]}"
                            else:
                                data_text = f"text={data[6]}"

                            database.add_item_data(new_item, data_text)

                        print(f"[INFO] Товар '{item[1]}' перенесен")
                category_id += 1

    def copy_stat(self):
        """
        Перенос покупок

        :return:
        """
        with self.open_old() as db:
            cur = db.cursor()
            old_sales = cur.execute("SELECT * FROM Sales").fetchall()

            for sale in old_sales:
                purchase_data = dict()
                purchase_data['user_id'] = sale[0]
                purchase_data['item_name'] = sale[1]

                old_date = sale[6]
                old = datetime.strptime(old_date, "%d/%m/%Y")

                purchase_data['date'] = old.strftime("%d/%m/%Y")

                # проверка на несколько покупок
                some_purchase = cur.execute("SELECT * FROM Sales WHERE comment = ?", [sale[3]]).fetchall()

                purchase_data['amount'] = int(sale[4]) * len(some_purchase)
                purchase_data['count'] = len(some_purchase)

                sale_id = database.add_buy(purchase_data)

                for purchase in some_purchase:
                    # запись покупок в новую БД
                    database.old_sold_buy(sale_id, purchase[5])


# # # Старт скрипта # # #

print("Перенос данных со старой версии Gonal Bot")

if not os.path.exists("shop.sqlite"):
    print("БД старой версии отсутствует! Проверьте еще раз и запустите снова")
    sys.exit()

time.sleep(0.5)
print("Старая БД найдена!")

if not os.path.exists("shopDB.sqlite"):
    print("БД новой версии отсутствует! Проверьте еще раз и запустите снова")
    sys.exit()

time.sleep(0.5)
print("Новая БД найдена!")

shop_db = Database()

# # # Начало переноса данных # # #
time.sleep(1)
print("Дальше потребуется ввод данных: Y - Да; N - нет")
time.sleep(1)

# пользователи
print("Перенести список пользователей?")
users: str = input()

if users.lower() == "y":
    print("Начало переноса...")
    shop_db.copy_users()
    print("Перенос завершен!")

time.sleep(0.5)
# кошельки
print("Перенести данные о кошельках?")
payment: str = input()

if payment.lower() == "y":
    print("Начало переноса...")
    shop_db.copy_payment()
    print("Перенос завершен!")

time.sleep(0.5)
# faq
print("Перенести FAQ?")
faq: str = input()

if faq.lower() == "y":
    print("Начало переноса...")
    shop_db.copy_faq()
    print("Перенос завершен!")

time.sleep(0.5)
# весь ассортимент
print("Перенести весь ассортимент?")
items: str = input()

if items.lower() == "y":
    print("Начало переноса...")

    print("Перенос категорий...")
    shop_db.copy_categories()

    print("Перенос подкатегорий...")
    shop_db.copy_subcategories()

    print("Перенос товаров...")
    shop_db.copy_items()
    print("Перенос завершен!")

time.sleep(0.5)
# весь ассортимент
print("Перенести все покупки?")
sales: str = input()

if sales.lower() == "y":
    print("Начало переноса...")
    shop_db.copy_stat()
    print("Перенос завершен!")
