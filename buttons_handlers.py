from wx import MessageBox, OK
from api_handler import choose_api_mode
from database_manager import Dota2TournamentsDataBase
from database_requests import truncate_stats
from convert_to_xlsx import convert_stats_from_db


async def main(match_id, path, sourse, mode, database_name):
    '''Обработчик главной кнопки

        Args:
            match_id (int): ID матча для получения статистики
            path (str): Путь для сохранения Excel-файла
            sourse (str): Источник откуда берётся статистика:
                - 'api'
                - 'db': База Данных
            mode (str): Режим работы:
                - 'excel-no-db':  Записать в Excel, не записывать в БД
                - 'excel-db':  Записать в Excel, записать в БД
                - 'no-excel-db': Не записывать в Excel, записать в БД
            database_name (str): Имя базы данных
    '''

    match sourse:
        case 'api':
            #Когда нужно извлечь данные из api
            await choose_api_mode(match_id, path, mode, database_name)
        case 'db':
            #Когда нужно извлечь данные из базы данных
            convert_stats_from_db(match_id, path, database_name)


def clean_db(database_name):
    '''
        Обработчик кнопки "Очистить Базу Данных"

        Args:
            database_name (str): Имя базы данных
    '''

    try:
        db = Dota2TournamentsDataBase(database_name)
        truncate_stats(db)
        MessageBox(f'База данных {database_name} очищена', caption='Внимание', style=OK)
    except:
        MessageBox(f'Не удалось очистить базу данных {database_name}', caption='Внимание', style=OK)