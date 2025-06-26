import psycopg2


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

    def get_companies_and_vacancies_count(self):
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            # cur.execute(f"SELECT * FROM {self.employers_table_name}")
            cur.execute("SELECT e.employer_name, COUNT(v.vacancy_id) AS vacancy_count "
                        "FROM employers e "
                        "LEFT JOIN vacancies v ON e.employer_id = v.employer_id "
                        "GROUP BY e.employer_name")
            rows = cur.fetchall()
            for row in rows:
                print(row)
                input()
