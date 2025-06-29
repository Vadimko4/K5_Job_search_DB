import time
from datetime import timedelta

from src.hh_handler import HhHandler
import psycopg2


def user_menu_out():
    """Функция выводит главное меню программы"""
    print("\nВыберите дальнейшее действие")
    print("""\n1. Вывести список компаний с указанием количества вакансий в текущей таблице
2. Вывести список всех вакансий в текущей таблице
3. Получить среднюю зарплату по вакансиям текущей таблицы
4. Вывести список вакансий, у которых зарплата выше средней по вакансиям текущей таблицы
5. Отфильтровать и вывести вакансии, в названии которых содержится ключевое слово
6. Сбросить фильтры на вакансии в текущей таблице
7. Выход из программы""")


def foolproof_user_menu_input(menu_range_input: list[str]) -> str:
    """
    Функция выбора пользователя пункта меню - принимает от пользователя только
    цифры, которые содержатся в menu_range_input
    """
    while True:
        user_answer = input('\nПользователь: ')
        if len(user_answer) != 1 or user_answer not in menu_range_input:
            print(f"\nПрограмма: Неверный ввод, вам нужно ввести значение от {menu_range_input[0]} "
                  f"до {menu_range_input[-1]} \nПопробуйте ещё раз")
        else:
            break
    return user_answer


def time_delay(delta_t: timedelta, delay_amount: int) -> None:
    """
    Вспомогательная сервисная функция задержки времени.
    Нужна для того, чтобы сообщения в консоли не мельтешили и их комфортно было читать.
    Если разница delta_t меньше delay_amount секунд, то программа ждёт delay_amount
    дополнительных секунды
    """
    if delta_t.days == 0 and delta_t.seconds < delay_amount:
        time.sleep(delay_amount)


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц, для сохранения данных о работодателях и вакансиях"""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE employers (                        
                        employer_id INTEGER PRIMARY KEY,
                        employer_name VARCHAR(255) NOT NULL,
                        employer_url TEXT,
                        open_vacancies INTEGER
                    )
                """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id),
                vacancy_name VARCHAR,
                vacancy_url TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                description TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(hh_object: HhHandler, database_name: str, params: dict) -> None:
    """Сохранение данных о работодателях и вакансиях в базу данных"""
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        # Сохранение данных о работодателях
        for employer in hh_object.employers:
            cur.execute(
                """
                INSERT INTO employers (employer_id, employer_name, employer_url, open_vacancies)
                VALUES (%s, %s, %s, %s)
                """,
                (employer['emp_hh_id'], employer['emp_name'], employer['emp_url'], employer['vac_count'])
            )

            # Сохранение данных о вакансиях
        for vacancy in hh_object.vacancies:
            cur.execute(
                """
                INSERT INTO vacancies (employer_id, vacancy_name, vacancy_url, 
                salary_from, salary_to, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING vacancy_id
                """,
                (vacancy['employer_id'], vacancy['vacancy_name'], vacancy['vacancy_url'],
                 vacancy['salary_from'], vacancy['salary_to'], vacancy['description'])
            )

        conn.commit()
        conn.close()