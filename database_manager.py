import os
from dotenv import load_dotenv
import psycopg2
from wx import MessageBox, OK


class Dota2TournamentsDataBase:
    '''
        Класс для управления базой данных турниров по Dota 2
        Обеспечивает подключение к базе данных, выполнение SQL-запросов и управление данными
    '''

    def __init__(self, database_name):
        '''
            Инициализирует объект класса и устанавливает соединение с базой данных

            Args:
                database_name (str): Имя базы данных, к которой нужно подключиться
        '''

        self.database_name = database_name
        self.tournament_db = self.connect_to_database()

    def connect_to_database(self):
        '''
        Устанавливает соединение с базой данных PostgreSQL

        Returns:
            psycopg2.connection: Объект соединения с базой данных
        '''

        try:
            load_dotenv()  #Используется, чтобы получить доступ к .env, где прописаны настройки для подключения к базе данных
            default_db_connection = psycopg2.connect(
                host=os.getenv('HOST'),
                port=os.getenv('PORT'),
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                database=self.database_name
            )
            default_db_connection.autocommit = True
            return default_db_connection

        except psycopg2.Error as err:
            MessageBox(f'Создайте базу данных {self.database_name}, например, используя pgAdmin', caption='Ошибка', style=OK)


    def request_handler(self, sql_request, params=None):
        '''
        Выполняет SQL-запрос с защитой от SQL-инъекций

        Args:
            sql_request (str): SQL-запрос для выполнения
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None
        '''

        try:
            with self.tournament_db.cursor() as cur:
                cur.execute(sql_request, params or ())
        except psycopg2.Error as err:
            MessageBox(f'Ошибка при выполнении запроса: {err}', caption='Ошибка', style=OK)


    @staticmethod
    def extract_team_stats(match_id):
        '''
            Формирует SQL-запрос для получения статистики команд по match_id

            Args:
                match_id (str): Идентификатор матча

            Returns:
                tuple: SQL-запрос и параметры для выполнения
        '''

        query = '''
                SELECT score, name, winner
                FROM teams_stats
                WHERE match_id = %s
                '''
        return query, (match_id,)


    @staticmethod
    def extract_players_stats(match_id):
        '''
            Формирует SQL-запрос для получения статистики игроков по match_id

            Args:
                match_id (str): Идентификатор матча

            Returns:
                tuple: SQL-запрос и параметры для выполнения
        '''

        query = '''
                SELECT name, hero, team, kills, assists, deaths, net_worth, last_hits, denies, gold_per_min, xp_per_min, hero_damage, tower_damage, hero_healing, obs_placed, sen_placed
                FROM players_stats
                WHERE match_id = %s
                ORDER BY team, kills DESC
                '''
        return query, (match_id,)


    @staticmethod
    def insert_team_stats(teams_stats, match_id):
        '''
            Формирует SQL-запрос для вставки статистики команд

            Args:
                teams_stats (dict): Словарь с данными о командах
                match_id (str): Идентификатор матча

            Returns:
                tuple: SQL-запрос и параметры для выполнения
        '''

        query = '''
                INSERT INTO teams_stats (match_id, score, name, winner) 
                VALUES (%s, %s, %s, %s)
                '''
        params = []

        for single_team_stats in teams_stats.values():
            params.append(
                (
                    match_id,
                    single_team_stats['score'],
                    single_team_stats['name'],
                    single_team_stats['winner']
                )
            )
        return query, params

    @staticmethod
    def insert_players_stats(players_stats, match_id):
        '''
        Формирует SQL-запрос для вставки статистики игроков

        Args:
            players_stats (dict): Словарь с данными об игроках
            match_id (str): Идентификатор матча

        Returns:
            tuple: SQL-запрос и параметры для выполнения
        '''

        query = '''
        INSERT INTO players_stats (player_id, match_id, name, hero, team, kills, assists, deaths, net_worth,
        last_hits, denies, gold_per_min, xp_per_min, hero_damage,
        tower_damage, hero_healing, obs_placed, sen_placed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        params = []
        for player_id, single_player_stats in players_stats.items():
            params.append((
                player_id, match_id, single_player_stats['name'], single_player_stats['hero'],
                single_player_stats['team'],
                single_player_stats['kills'], single_player_stats['assists'], single_player_stats['deaths'],
                single_player_stats['net_worth'], single_player_stats['last_hits'], single_player_stats['denies'],
                single_player_stats['gold_per_min'], single_player_stats['xp_per_min'],
                single_player_stats['hero_damage'],
                single_player_stats['tower_damage'], single_player_stats['hero_healing'],
                single_player_stats['obs_placed'],
                single_player_stats['sen_placed']
            ))
        return query, params

    @staticmethod
    def create_team_stats_table():
        '''
            Формирует SQL-запрос для создания таблицы статистики команд

            Returns:
                str: SQL-запрос для выполнения
        '''

        return '''
         CREATE TABLE IF NOT EXISTS teams_stats (
         match_id BIGINT,
         score INT,
         name TEXT,
         winner BOOLEAN,
         PRIMARY KEY (match_id, name)
        );
        '''

    @staticmethod
    def create_players_stats_table():
        '''
            Формирует SQL-запрос для создания таблицы статистики игроков

            Returns:
                str: SQL-запрос для выполнения
        '''

        return '''
            CREATE TABLE IF NOT EXISTS players_stats
            (
                player_id BIGINT,
                match_id BIGINT,
                name text, 
                hero text, 
                team text, 
                kills int, 
                assists int, 
                deaths int, 
                net_worth int,
                last_hits int, 
                denies int, 
                gold_per_min int, 
                xp_per_min int, 
                hero_damage int,
                tower_damage int, 
                hero_healing int, 
                obs_placed int, 
                sen_placed int,
                PRIMARY KEY (match_id, player_id)
            );
            '''


    @staticmethod
    def truncate_tables():
        '''
            Формирует SQL-запрос для очистки таблиц статистики

            Returns:
                str: SQL-запрос для выполнения
            '''

        return '''
        TRUNCATE teams_stats;
        TRUNCATE players_stats;
        '''