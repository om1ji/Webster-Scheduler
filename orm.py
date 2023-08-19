import sqlite3

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
    conn.commit()

# Вставка данных
def insert(user_id: str, user_name: str, file_link: str) -> bool:
    select_query = '''
        SELECT * FROM users WHERE user_id = ?;
    '''
    cursor.execute(select_query, (user_id,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        update_data_query = '''
            UPDATE users SET file_id = ? WHERE user_id = ?;
        '''
        cursor.execute(update_data_query, (file_link, user_id))
        conn.commit()
        print(f"File ID для пользователя {user_id} обновлен.")
    else:
        insert_data_query = '''
            INSERT INTO users (username, user_id, file_id) VALUES (?, ?, ?);
        '''
        user_data = (user_name, user_id, file_link)
        cursor.execute(insert_data_query, user_data)
        conn.commit()
        print(f"Новая запись добавлена для пользователя {user_id}.")
    
    return existing_record

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