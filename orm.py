import sqlite3
import ast

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Dict

conn = sqlite3.connect('webster.db')
cursor = conn.cursor()

def create_users_table() -> None:
    create_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                username TEXT,
                file_id TEXT,
                notification_time TEXT,
                qr TEXT,
                UNIQUE(user_id, file_id, qr)
            );
        '''
    
    cursor.execute(create_table_query)
    conn.commit()

def create_schedule_table() -> None:
    create_table_query = '''
            CREATE TABLE IF NOT EXISTS week_schedule (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                monday TEXT,
                tuesday TEXT,
                wednesday TEXT,
                thursday TEXT,
                friday TEXT
            );
            '''
    
    cursor.execute(create_table_query)
    conn.commit()

def create_jobs_table() -> None:
    create_jobs_table_query = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            text TEXT,
            day_of_week TEXT,
            time INTEGER
        );
        """
    
    cursor.execute(create_jobs_table_query)
    conn.commit()

def create_tables() -> None:
    create_users_table()
    create_schedule_table()
    create_jobs_table()

# Вставка данных в таблицу users
def insert(user_id: int, user_name: str, file_id: str, schedule: Dict[str, str]) -> bool:
    """Делает запись в базу данных. Создаёт новую, если пользователя нет в базе. 
    Обновляет, если пользователь уже есть

    Args:
        user_id (int): User ID пользователя в Telegram
        user_name (str): Username пользователя (@user)
        file_id (str): ID файла, присваиваемый Телеграмом
        schedule (Dict[str, str]): Словарь, хранящий в себе расписание на каждый день недели

    Returns:
        bool: True, если пользователь уже был в базе и произошло обновление записи. 
        False, если пользователя не было и была внесена новая запись
    """
    select_query = '''
        SELECT * FROM users WHERE user_id = ?;
    '''
    cursor.execute(select_query, (user_id,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        update_data_query = '''
            UPDATE users SET file_id = ? WHERE user_id = ?;
        '''
        cursor.execute(update_data_query, (file_id, user_id))
        conn.commit()

        query = '''
            UPDATE week_schedule SET monday = ?, tuesday = ?, wednesday = ?, thursday = ?, friday = ?
            WHERE user_id = ?;'''
        
        print(f"File ID для пользователя {user_id} обновлен.")

        cursor.execute(query, (schedule["monday"],
                                schedule["tuesday"],
                                schedule["wednesday"],
                                schedule["thursday"],
                                schedule["friday"],
                                user_id))
        conn.commit()

    else:
        insert_data_query = '''
            INSERT INTO users (username, user_id, file_id) VALUES (?, ?, ?);
        '''

        user_data = (user_name, user_id, file_id)
        cursor.execute(insert_data_query, user_data)
        conn.commit()

        query = '''
            INSERT INTO week_schedule (user_id, monday, tuesday, wednesday, thursday, friday)
            VALUES (?, ?, ?, ?, ?, ?);
        '''
        
        cursor.execute(query, (user_id,
                                schedule["monday"],
                                schedule["tuesday"],
                                schedule["wednesday"],
                                schedule["thursday"],
                                schedule["friday"]))
        conn.commit()

        print(f"Новая запись добавлена для пользователя {user_id}.")

    return existing_record

def get_day_schedule(user_id: int, day: str) -> list:
    
    """Извлекает данные из базы данных о расписании в зависимости от указанного дня недели

    Args:
        user_id (int): User ID пользователя в Telegram 
        day (str): День недели ("monday", "tuesday", ...)
    Returns:
        list: Список занятий на указанный день недели

    """    
    query = """SELECT {} FROM week_schedule WHERE user_id = ?""".format(day)
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    if result:
        return result
    else:
        return None

# Jobs

def save_job(user_id: int, text: str, day_of_week: str, time: int) -> None:
    query_select = "SELECT * FROM jobs WHERE user_id = ? AND text = ? AND day_of_week = ? AND time = ?"
    cursor.execute(query_select, (user_id, text, day_of_week, time))
    existing_record = cursor.fetchone()
    
    if not existing_record:
        query_insert = "INSERT INTO jobs (user_id, text, day_of_week, time) VALUES (?, ?, ?, ?)"
        cursor.execute(query_insert, (user_id, text, day_of_week, time))
        conn.commit()

def delete_job(user_id: int, text: str, day_of_week: str, time: int) -> None:
    query_delete = "DELETE FROM jobs WHERE user_id = ? AND text = ? AND day_of_week = ? AND time = ?"
    cursor.execute(query_delete, (user_id, text, day_of_week, time))
    conn.commit()

def get_jobs() -> list:
    """Возвращает список асинхронных задач"""
    query = "SELECT * FROM jobs"
    cursor.execute(query)
    return cursor.fetchall()
    
def get_job(user_id: int, text: str, day_of_week: str = None, time: int = None) -> list:
    query = 'SELECT day_of_week, time FROM jobs WHERE user_id = ? AND text = ?'
    
    if time and day_of_week:
        query = "SELECT * FROM jobs WHERE user_id = ? AND text = ? AND day_of_week = ? AND time = ?"
        cursor.execute(query, (user_id, text, day_of_week, time))
        result = cursor.fetchone()
    else:
        cursor.execute(query, (user_id, text))
        result = cursor.fetchall()

    return result

def delete_all_jobs(user_id: int) -> None:
    query = "DELETE FROM jobs WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    conn.commit()

def check_user_for_presence(user_id: int) -> bool:
    query = "SELECT * FROM users WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result

def check_qr_for_presence(user_id: int) -> str:
    query = "SELECT qr FROM users WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def upload_qr(user_id: int, file_id: str) -> None:
    query = "UPDATE users SET qr = ? WHERE user_id = ?"
    cursor.execute(query, (file_id, user_id,))
    conn.commit()