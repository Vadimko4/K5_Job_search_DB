import psycopg2
from typing import Any


VACANCY_PER_PAGE_OUT = 5


class DBManager:
    """
    Класс для работы с БД hhvacancies
    """

    def __init__(self, params: dict):
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
        """Получает список всех компаний и количество вакансий в базе у каждой компании"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("SELECT e.employer_name, COUNT(v.vacancy_id) AS vacancy_count "
                        "FROM employers e "
                        "LEFT JOIN vacancies v ON e.employer_id = v.employer_id "
                        "GROUP BY e.employer_name")
            rows = cur.fetchall()
            print(f'\n{'-' * 150}')
            for row in rows:
                print(f'Компания: {row[0]}\nВакансий: {row[1]}\n{'-' * 150}')

        conn.close()

    def get_all_vacancies(self) -> None:
        """
        Получает список всех вакансий в базе с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, vacancy_url "
                        "FROM employers e "
                        "LEFT JOIN vacancies v ON e.employer_id = v.employer_id")
            rows = cur.fetchall()
            if not rows:
                print("\nПрограмма: в базе нет ни одной вакансии.")
            else:
                self.print_vacancies(rows)

        conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> None:
        """
        Получает список всех вакансий, в названии которых содержится ключевое слово keyword.
        Регистр значения не имеет
        """
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("SELECT e.employer_name, v.vacancy_name, v.salary_from, v.salary_to, vacancy_url "
                        "FROM employers e "
                        "LEFT JOIN vacancies v ON e.employer_id = v.employer_id "
                        "WHERE v.vacancy_name ILIKE %s", ('%' + keyword + '%',))
            rows = cur.fetchall()
            if not rows:
                print("\nПрограмма: нет ни одной вакансии по Вашему запросу.")
            else:
                print(f"\nПрограмма: по Вашему запросу найдено {len(rows)} вакансий.")
                self.print_vacancies(rows)

        conn.close()
