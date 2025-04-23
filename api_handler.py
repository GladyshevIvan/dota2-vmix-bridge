from wx import MessageBox, OK
from get_stats import get_match_stats_from_api
from database_manager import Dota2TournamentsDataBase
from database_requests import create_tables, insert_stats
from convert_to_xlsx import convert_stats_from_api


async def choose_api_mode(match_id, path, mode, database_name):
    '''
    Получает статистику из API по match_id и записывает или не записывает её в Excel-файл и/или Базу Данных
    в зависимости от выбранноой опции mode

    Args:
        match_id (int): ID матча для получения статистики
        path (str): Путь для сохранения Excel-файла
        mode (str): Режим работы:
            - 'excel-no-db':  Записать в Excel, не записывать в БД
            - 'excel-db':  Записать в Excel, записать в БД
            - 'no-excel-db': Не записывать в Excel, записать в БД
        database_name (str): Имя базы данных
    '''

    data, match_id = await get_match_stats_from_api(match_id) #Получение статистики матча

    if mode in ('excel-no-db', 'excel-db'):
        #Записать в эксель
        convert_stats_from_api(data, path)

    if mode in ('excel-db', 'no-excel-db'):
        #Записать в Базу Данных
        db = Dota2TournamentsDataBase(database_name)
        create_tables(db)
        insert_stats(db, data, match_id)