from src.hh_handler import HhHandler
import psycopg2
from src.config import config


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


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о каналах и видео в базу данных"""
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        for channel in data:
            channel_data = channel['channel']['snippet']
            channel_stats = channel['channel']['statistics']
            cur.execute(
                """
                INSERT INTO channels (title, views, subscribers, videos, channel_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING channel_id
                """,
                (channel_data['title'], channel_stats['viewCount'], channel_stats['subscriberCount'],
                 channel_stats['videoCount'], f"https://www.youtube.com/channel/{channel['channel']['id']}")
            )
            channel_id = cur.fetchone()[0]

            videos_data = channel['videos']
            for video in videos_data:
                video_data = video['snippet']
                cur.execute(
                    """
                    INSERT INTO videos (channel_id, title, publish_date, video_url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (channel_id, video_data['title'], video_data['publishedAt'],
                     f"https://www.youtube.com/watch?v={video['id']['videoId']}")
                )

        conn.commit()
        conn.close()


def main():
    """Основная функция программы - точка входа в проект"""

    my_hh = HhHandler()
    print("\nПрограмма: подождите, получаю общую информацию о выбранных работодателях c www.hh.ru...")
    my_hh.get_employers_info()
    print("Данные успешно получены")

    print("\nПрограмма: теперь собираю данные о вакансиях этих работодателей c www.hh.ru\n"
          "Обычно это происходит чуть дольше - немного терпения... ")
    my_hh.get_vacancies_info()
    print("\nИнформация успешно получена: ")
    print(f'нашла для вас {len(my_hh.vacancies)} вакансий')

    print("\nСекунду, сформирую из полученной информации базу данных... ")
    params = config()
    create_database('hhvacancies', params)
    print("База данных создана")

    print("\nНаполняю её информацией... ")
    save_data_to_database(my_hh, 'hhvacancies')


if __name__ == '__main__':
    main()

