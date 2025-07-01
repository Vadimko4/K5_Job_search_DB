from typing import Any

import psycopg2

VACANCY_PER_PAGE_OUT = 5


class DBManager:
    """
    Класс для работы с БД hhvacancies
    """

    def __init__(self, params: dict) -> None:
        """Конструктор класса"""
        self.database_name = "hhvacancies"
        self.employers_table_name = "employers"
        self.vacancies_table_name = "vacancies"
        self.params = params

    @staticmethod
    def print_vacancies(vacancies: list[tuple[Any]]) -> None:
        """
        Сервисная функция.
        Выводит список вакансий в удобном для чтения виде.
        """
        cnt = 0
        print(f'\n{'-' * 150}')
        for vac in vacancies:
            if not vac[2]:
                salary_from = 'не указана'
            else:
                salary_from = vac[2]
            if not vac[3]:
                salary_to = 'не указана'
            else:
                salary_to = vac[3]
            print(f"Компания: {vac[0]} \nВакансия: {vac[1]} \nЗарплата от: {salary_from}\n"
                  f"Зарплата до: {salary_to} \nСсылка на вакансию: {vac[4]} \n{'-' * 150}")
            cnt += 1
            if cnt % VACANCY_PER_PAGE_OUT == 0:
                user_input = input("<q> - возврат в главное меню, остальное - продолжить вывод: ").lower()
                if user_input == 'q':
                    return

    def get_companies_and_vacancies_count(self) -> None:
        """Получает список всех компаний и количество вакансий в базе у каждой компании в таблице текущих вакансий"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT employer_name, COUNT(vacancy_name) AS vacancy_count FROM current_vacancies
                GROUP BY employer_name
            """)
            rows = cur.fetchall()
            print(f'\n{'-' * 150}')
            for row in rows:
                print(f'Компания: {row[0]}\nВакансий: {row[1]}\n{'-' * 150}')

        conn.close()

    def get_all_vacancies(self) -> int:
        """
        Получает и выводит список всех вакансий в таблице текущих вакансий
        с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        Возвращает количество вакансий в таблице текущих вакансий.
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM current_vacancies")
            rows = cur.fetchall()
            vacancies_count = len(rows)
            if not rows:
                print("\nПрограмма: в базе нет ни одной вакансии.")
            else:
                self.print_vacancies(rows)

        conn.close()
        return vacancies_count

    def get_vacancies_with_keyword(self, keyword: str) -> int:
        """
        Получает и выводит список всех вакансий в таблице текущих вакансий,
        в названии которых содержится ключевое слово keyword.
        Регистр значения не имеет. Обновляет таблицу текущих вакансий.
        Возвращает количество вакансий в таблице текущих вакансий.
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS current_vacancies")
            # Создаём таблицу текущих вакансий, отфильтрованных из всей базы по ключевому слову
            cur.execute("""
                CREATE TABLE current_vacancies AS
                SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, v.vacancy_url
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                WHERE v.vacancy_name ILIKE %s
            """, ('%' + keyword + '%',))

            # Выводим результат запроса
            cur.execute("SELECT * FROM current_vacancies")
            rows = cur.fetchall()
            vacancies_count = len(rows)
            if not rows:
                print("\nПрограмма: нет ни одной вакансии по Вашему запросу.")
            else:
                print(f"\nПрограмма: по Вашему запросу найдено {len(rows)} вакансий.")
                self.print_vacancies(rows)

        conn.commit()
        conn.close()
        return vacancies_count

    def get_avg_salary(self) -> None:
        """Получает среднюю зарплату по вакансиям в текущей таблице вакансий."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, salary_from)) / 2)
                FROM current_vacancies
            """)
            row = cur.fetchone()
            print(f'\nПрограмма: средняя зарплата по вакансиям базы составляет {int(float(row[0]))} руб')

        conn.close()

    def get_vacancies_with_higher_salary(self) -> None:
        """
        Получает и выводит список всех вакансий в текущей таблице, у которых зарплата выше средней по всем вакансиям
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM current_vacancies
                WHERE salary_from > (
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, salary_from)) / 2)
                    FROM current_vacancies)
                OR
                    salary_to > (
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, salary_from)) / 2)
                    FROM current_vacancies)
            """)
            rows = cur.fetchall()
            vacancies_count = len(rows)
            if not vacancies_count:
                print("\nПрограмма: в текущей таблице нет ни одной подходящей вакансии.")
            else:
                print(f"\nПрограмма: по Вашему запросу найдено {vacancies_count} вакансий.")
                self.print_vacancies(rows)

        conn.close()

    def reset_current_vacancies(self) -> int:
        """
        Сбрасывает таблицу текущих вакансий к первоначальному состоянию,
        когда в ней отображены все вакансии базы данных, без учёта фильтров.
        В таблице текущих вакансий указаны название компании,
        название вакансии, зарплата и ссылка на вакансию.
        Возвращает количество вакансий в таблице текущих вакансий.
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS current_vacancies")
            cur.execute("""
                CREATE TABLE current_vacancies AS
                SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, vacancy_url
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id""")
            cur.execute("SELECT * FROM current_vacancies")
            rows = cur.fetchall()
            vacancies_count = len(rows)

        conn.commit()
        conn.close()
        return vacancies_count
