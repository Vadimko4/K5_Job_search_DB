import datetime
import time

from src.hh_handler import HhHandler
from src.db_manager import DBManager
from src.config import config
from src.utils import (create_database, save_data_to_database, time_delay,
                       user_menu_out, foolproof_user_menu_input)


def main():
    """Основная функция программы - точка входа в проект"""

    my_hh = HhHandler()
    print("\nПрограмма: подождите, получаю общую информацию о выбранных работодателях c www.hh.ru...")
    time1 = datetime.datetime.now()
    my_hh.get_employers_info()
    time2 = datetime.datetime.now()
    time_delay(time2 - time1, 2)
    print("Данные успешно получены")

    print("\nПрограмма: теперь собираю данные о вакансиях этих работодателей c www.hh.ru\n"
          "Обычно это происходит чуть дольше - немного терпения... ")
    time1 = datetime.datetime.now()
    my_hh.get_vacancies_info()
    time2 = datetime.datetime.now()
    time_delay(time2-time1, 2)
    print("\nИнформация успешно получена: ")
    print(f'нашла для вас {len(my_hh.vacancies)} вакансий')

    print("\nПрограмма: секунду, сформирую из полученной информации базу данных... ")
    time1 = datetime.datetime.now()
    params = config()
    create_database("hhvacancies", params)
    time2 = datetime.datetime.now()
    time_delay(time2 - time1, 2)
    print("База данных создана")

    print("\nПрограмма: наполняю её информацией... ")
    time1 = datetime.datetime.now()
    save_data_to_database(my_hh, 'hhvacancies', params)
    time2 = datetime.datetime.now()
    time_delay(time2 - time1, 2)
    print("База данных готова!")
    # Создаём объект класса DBManager, который будет обрабатывать созданную БД
    my_db_manager = DBManager(params)

    # Реализация меню пользователя
    quit_flag = False
    while not quit_flag:
        print(f"\nКоличество отслеживаемых компаний: {len(my_hh.employers)}")
        print(f"Вакансий в базе: {len(my_hh.vacancies)}")
        user_menu_out()

        user_input = foolproof_user_menu_input(list('123456'))
        if user_input == '1':  # список всех компаний с указанием количеством вакансий в базе
            my_db_manager.get_companies_and_vacancies_count()

        if user_input == '2':  # список всех вакансий в базе
            my_db_manager.get_all_vacancies()

        if user_input == '3':  # средняя зарплата по имеющимся вакансиям
            top_amount = foolproof_user_top_amount_input(len(vacancies))
            vacancies = sort_vacancies_by_salary_decrease(vacancies)
            top_vacancies = get_top_vacancies(vacancies, top_amount)
            print_vacancies(top_vacancies)

        if user_input == '4':  # список вакансий, у которых зарплата выше средней по всем вакансиям
            print_vacancies(vacancies)

        if user_input == '5':  # список вакансий, в названии которых содержится ключевое слово
            print("\nПрограмма: через пробел введите ключевые слова для поиска в описании вакансии")
            user_answer = input('Пользователь: ').lower()
            vacancies, file_object, is_primary_vacancies_update = file_user_menu(vacancies, file_object)
            if is_primary_vacancies_update:
                primary_vacancies = vacancies

        if user_input == '6':  # Выход из программы
            print("\nПрограмма: Всего доброго!")
            quit_flag = True


if __name__ == '__main__':
    main()

