import sqlite3
from threading import Lock

class DatabaseManager:
    def __init__(self, db_name='chatgpttelegrambot.db'):
        self.db_name = db_name
        self.lock = Lock()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                tg_id INTEGER UNIQUE
                            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                                id INTEGER PRIMARY KEY,
                                tg_id INTEGER,
                                prompt TEXT,
                                result TEXT
                            )''')
            conn.commit()
            conn.close()

    def add_user(self, tg_id):
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (tg_id) VALUES (?)", (tg_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                print(e)

    def add_result(self, tg_id, prompt, result):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO results (tg_id, prompt, result) VALUES (?, ?, ?)", (tg_id, prompt, result))
            conn.commit()
            conn.close()

    def get_total_users(self):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            conn.close()
            return total_users

# Создание экземпляра менеджера базы данных
db_manager = DatabaseManager()
