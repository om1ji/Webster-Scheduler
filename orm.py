import sqlite3

from typing import Dict

conn = sqlite3.connect('webster.db')
cursor = conn.cursor()

# Создание таблицы
def create():
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            file_id TEXT,
            UNIQUE(user_id, file_id)
        );
    '''
    cursor.execute(create_table_query)

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS schedule (
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
            UPDATE schedule SET monday = ?, tuesday = ?, wednesday = ?, thursday = ?, friday = ?
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
            INSERT INTO schedule (user_id, monday, tuesday, wednesday, thursday, friday)
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

def get_day_schedule(user_id: int, day: str) -> str:
    
    """Извлекает данные из базы данных о расписании в зависимости от указанного дня недели

    Args:
        user_id (int): User ID пользователя в Telegram 
        day (str): День недели ("monday", "tuesday", ...)
    Returns:
        str: Список занятий на указанный день недели

    """    
    query = """SELECT {} FROM schedule WHERE user_id = ?""".format(day)
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    if result:
        return result[0][0]
    else:
        return None

# Выборка данных
def select_all() -> list:
    users = []
    select_query = '''
        SELECT * FROM users;
    '''
    cursor.execute(select_query)
    result = cursor.fetchall()
    for row in result:
        users.append

def select_file_id(user_id: int) -> str:
    select_query = """SELECT file_id FROM users WHERE user_id = ?"""
    cursor.execute(select_query, (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def check_for_prescense(user_id: int) -> bool:
    query = """SELECT * FROM users WHERE user_id = ?"""
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    print(result)
    if result:
        return True
    else:
        return False
