import time
from datetime import timedelta

from src.hh_handler import HhHandler
import psycopg2


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

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur: # employer_num SERIAL PRIMARY KEY,
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
        # Сохранение данных о работодателях RETURNING employer_id
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