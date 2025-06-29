"""Модуль с классом для работы с API HH"""
# from http.client import responses
# import time
# import random

import requests
from src.config import employers
from src.db_manager import VACANCY_PER_PAGE_OUT

access_token = 'USERH2FNOK2KS7NPVHU2SQG4V2C05906OGGM0EM0TN566KHGBM8APFK3D3ULI11J'

API_VACANCY_PER_PAGE = 2 # не более 100 - задаёт количество вакансий одного работодателя на страницу, всего 20 страниц


class ApiError(Exception):
    pass


class NotFoundError(ApiError):
    pass


class ServerError(ApiError):
    pass


class HhHandler:
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self):
        """Конструктор класса"""
        self.url_emp = 'https://api.hh.ru/employers'
        self.url_vac = 'https://api.hh.ru/vacancies'
        # self.headers = {'Authorization': f'Bearer {access_token}'}
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'page': 0, 'per_page': API_VACANCY_PER_PAGE} # получаем до API_VACANCY_PER_PAGE х 20 вакансий
                                                                    # от каждой компании работодателя
        self.employers = []
        self.vacancies = []

    def get_employers_info(self):
        """
        Получение информации о работодателях и количестве их вакансий
        с hh.ru - в формате списка словарей
        """
        for employer_id in employers:
            response = requests.get(f'{self.url_emp}/{employer_id}')
            self.employers.append(
                {
                    'emp_hh_id': employer_id,
                    'emp_name': response.json()['name'],
                    'emp_url': response.json()['alternate_url'],
                    'vac_count': response.json()['open_vacancies']
            })

    def get_vacancies_info(self):
        """
        Получение информации о всех вакансиях отслеживаемых 10-ти работодателей
        с hh.ru в формате JSON - в формате списка словарей
        """
        for employer_id in employers:
            self.params['employer_id'] = employer_id

            while self.params.get('page') != 20:
                response = requests.get(self.url_vac, headers=self.headers, params=self.params)
                status_code = response.status_code

                if 300 > status_code >= 200:
                    vacancies = response.json()['items']

                    # вытаскиваем из списка словарей с вакансиями только нужную нам информацию
                    new_vacancies = []
                    for vacancy_dict in vacancies:
                        name = vacancy_dict['name']
                        vacancy_url = vacancy_dict['alternate_url']
                        salary_info = vacancy_dict['salary']
                        # по поводу зарплаты рассматриваем разные случаи
                        if not salary_info:
                            salary_from = 0
                            salary_to = 0
                        else:
                            if vacancy_dict['salary']['from'] is None:
                                salary_from = 0
                            else:
                                salary_from = vacancy_dict['salary']['from']
                            if vacancy_dict['salary']['to'] is None:
                                salary_to = 0
                            else:
                                salary_to = vacancy_dict['salary']['to']
                        description = vacancy_dict['snippet']['requirement']

                        # формируем нужный нам словарь о вакансии
                        new_vacancy_dict = dict()
                        new_vacancy_dict['employer_id'] = employer_id
                        new_vacancy_dict['vacancy_name'] = name
                        new_vacancy_dict['vacancy_url'] = vacancy_url
                        new_vacancy_dict['salary_from'] = salary_from
                        new_vacancy_dict['salary_to'] = salary_to
                        new_vacancy_dict['description'] = description

                        new_vacancies.append(new_vacancy_dict)

                    self.vacancies.extend(new_vacancies)
                    self.params['page'] += 1

                elif 500 > status_code >= 400:
                    print(status_code)
                    print(response.json())
                    raise NotFoundError("Запрос содержит ошибку или неверные данные")

                elif 600 > status_code >= 500:
                    raise ServerError("На стороне сервера произошла ошибка при обработке запроса")

            self.params['page'] = 0

            # Пауза между запросами в секундах - когда не используем токен доступа к hh api
            # pause_duration = random.randint(2, 7)
            # time.sleep(pause_duration)
