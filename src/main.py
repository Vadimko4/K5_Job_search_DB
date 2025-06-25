import datetime
import time

from src.hh_handler import HhHandler
from src.config import config
from src.utils import create_database, save_data_to_database, time_delay


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
    create_database('hhvacancies', params)
    time2 = datetime.datetime.now()
    time_delay(time2 - time1, 2)
    print("База данных создана")

    print("\nПрограмма: наполняю её информацией... ")
    time1 = datetime.datetime.now()
    save_data_to_database(my_hh, 'hhvacancies', params)
    time2 = datetime.datetime.now()
    time_delay(time2 - time1, 2)
    print("База данных готова!")
    print(f"Количество отслеживаемых компаний: {len(my_hh.employers)}")
    print(f"Вакансий в базе: {len(my_hh.vacancies)}")


if __name__ == '__main__':
    main()

