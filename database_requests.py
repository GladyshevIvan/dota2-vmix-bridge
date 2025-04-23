from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation
from wx import MessageBox, OK


def create_tables(db):
    '''
    Создает таблицы для команд и игроков в базе данных

    Args:
        db (Dota2TournamentsDataBase): Объект для работы с базой данных
    '''

    db.request_handler(db.create_team_stats_table())
    db.request_handler(db.create_players_stats_table())


def insert_stats(db, data, match_id):
    '''
    Вставляет статистику команд и игроков в базу данных

    Args:
        db (Dota2TournamentsDataBase): Объект для работы с базой данных
        data (dict): Данные о матче
        match_id (str): Идентификатор матча
    '''

    try:
        #Вставка статистики команд
        query, params = db.insert_team_stats(data['teams_stats'], match_id)
        for p in params:
            db.request_handler(query, p)

        #Вставка статистики игроков
        query, params = db.insert_players_stats(data['players_stats'], match_id)
        for p in params:
            db.request_handler(query, p)

        MessageBox(f'Информация о матче добавлена в Базу Данных {db.database_name}', caption='Внимание', style=OK)
    except UniqueViolation as err:
        MessageBox(f'Матч с таким ID уже занесен в Базу Данных {db.database_name}', caption='Ошибка', style=OK)


def truncate_stats(db):
    '''
    Очищает таблицы в базе данных.

    Args:
        db (Dota2TournamentsDataBase): Объект для работы с базой данных
    '''

    db.request_handler(db.truncate_tables())


def show_match_stats(db, match_id):
    '''
    Получает статистику матча из базы данных

    Args:
        db (Dota2TournamentsDataBase): Объект для работы с базой данных
        match_id (str): Идентификатор матча

    Returns:
        dict: Словарь с данными о командах и игроках
    '''

    cursor = db.tournament_db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(*db.extract_team_stats(match_id))
    teams_stats = cursor.fetchall()
    cursor.execute(*db.extract_players_stats(match_id))
    players_stats = cursor.fetchall()
    return {'teams_stats': teams_stats, 'players_stats': players_stats}