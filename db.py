import sqlite3
from config import DB_NAME
from threading import Lock
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name=DB_NAME + '.db'):
        self.db_name = db_name
        self.lock = Lock()
    
    def create_tables(self):
        """Создаёт необходимые таблицы"""
        with self.lock, sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER UNIQUE NOT NULL,
                                requests INTEGER DEFAULT 3,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER NOT NULL,
                                prompt TEXT NOT NULL,
                                result TEXT NOT NULL,
                                prompt_tokens INTEGER DEFAULT 0,
                                completion_tokens INTEGER DEFAULT 0,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER NOT NULL,
                                amount INTEGER NOT NULL,
                                stars_paid INTEGER NOT NULL,
                                payment_id TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
            
            # Таблица промокодов
            cursor.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                code TEXT UNIQUE NOT NULL,
                                requests INTEGER NOT NULL,
                                max_uses INTEGER,
                                used INTEGER DEFAULT 0,
                                active INTEGER DEFAULT 1,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
            
            # Таблица активаций промокодов
            cursor.execute('''CREATE TABLE IF NOT EXISTS promo_activations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER NOT NULL,
                                promo_code TEXT NOT NULL,
                                requests_added INTEGER NOT NULL,
                                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
            
            conn.commit()
    
    def add_user(self, tg_id, initial_requests=3):
        """Добавляет нового пользователя с начальными запросами"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (tg_id, requests) VALUES (?, ?)", 
                    (tg_id, initial_requests)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"➕ Новый пользователь: {tg_id} (запросов: {initial_requests})")
        except Exception as e:
            print(f"❌ Ошибка при добавлении пользователя: {e}")
    
    def get_user_requests(self, tg_id):
        """Получает количество запросов пользователя"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT requests FROM users WHERE tg_id = ?", 
                    (tg_id,)
                )
                result = cursor.fetchone()
                if result:
                    return result[0]
                return 0
        except Exception as e:
            print(f"❌ Ошибка при получении запросов: {e}")
            return 0
    
    def use_request(self, tg_id):
        """Использует один запрос"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT requests FROM users WHERE tg_id = ?",
                    (tg_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                requests = result[0]
                
                if requests > 0:
                    cursor.execute(
                        "UPDATE users SET requests = requests - 1 WHERE tg_id = ?",
                        (tg_id,)
                    )
                    conn.commit()
                    return True
                
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при использовании запроса: {e}")
            return False
    
    def add_requests(self, tg_id, amount):
        """Добавляет запросы пользователю"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET requests = requests + ? WHERE tg_id = ?",
                    (amount, tg_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка при добавлении запросов: {e}")
            return False
    
    def add_payment(self, tg_id, amount, stars_paid, payment_id):
        """Сохраняет информацию о платеже"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payments (tg_id, amount, stars_paid, payment_id) VALUES (?, ?, ?, ?)",
                    (tg_id, amount, stars_paid, payment_id)
                )
                conn.commit()
        except Exception as e:
            print(f"❌ Ошибка при сохранении платежа: {e}")
    
    def add_result(self, tg_id, prompt, result, prompt_tokens=0, completion_tokens=0):
        """Сохраняет запрос пользователя и ответ бота с информацией о токенах"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO results (tg_id, prompt, result, prompt_tokens, completion_tokens) VALUES (?, ?, ?, ?, ?)", 
                    (tg_id, prompt, result, prompt_tokens, completion_tokens)
                )
                conn.commit()
        except Exception as e:
            print(f"❌ Ошибка при сохранении результата: {e}")
    
    def get_total_users(self):
        """Возвращает общее количество пользователей"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                return total_users
        except Exception as e:
            print(f"❌ Ошибка при получении количества пользователей: {e}")
            return 0
    
    def get_total_requests(self):
        """Возвращает общее количество запросов"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM results")
                total_requests = cursor.fetchone()[0]
                return total_requests
        except Exception as e:
            print(f"❌ Ошибка при получении количества запросов: {e}")
            return 0
    
    def get_total_revenue(self):
        """Возвращает общую выручку в звёздах"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(stars_paid) FROM payments")
                result = cursor.fetchone()[0]
                return result if result else 0
        except Exception as e:
            print(f"❌ Ошибка при получении выручки: {e}")
            return 0
    
    # ==================== ПРОМОКОДЫ ====================
    
    def create_promo(self, code, requests, max_uses=None):
        """Создаёт новый промокод"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO promo_codes (code, requests, max_uses) VALUES (?, ?, ?)",
                    (code.upper(), requests, max_uses)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            print(f"❌ Промокод {code} уже существует")
            return False
        except Exception as e:
            print(f"❌ Ошибка при создании промокода: {e}")
            return False
    
    def activate_promo(self, tg_id, code):
        """Активирует промокод для пользователя"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Проверяем существование промокода
                cursor.execute(
                    "SELECT requests, max_uses, used, active FROM promo_codes WHERE code = ?",
                    (code.upper(),)
                )
                promo = cursor.fetchone()
                
                if not promo:
                    return {'success': False, 'message': 'Промокод не найден'}
                
                requests, max_uses, used, active = promo
                
                if not active:
                    return {'success': False, 'message': 'Промокод деактивирован'}
                
                # Проверяем лимит использований
                if max_uses and used >= max_uses:
                    return {'success': False, 'message': 'Промокод исчерпан'}
                
                # Проверяем, активировал ли уже этот пользователь данный промокод
                cursor.execute(
                    "SELECT COUNT(*) FROM promo_activations WHERE tg_id = ? AND promo_code = ?",
                    (tg_id, code.upper())
                )
                
                if cursor.fetchone()[0] > 0:
                    return {'success': False, 'message': 'Вы уже использовали этот промокод'}
                
                # Начисляем запросы
                cursor.execute(
                    "UPDATE users SET requests = requests + ? WHERE tg_id = ?",
                    (requests, tg_id)
                )
                
                # Увеличиваем счетчик использований
                cursor.execute(
                    "UPDATE promo_codes SET used = used + 1 WHERE code = ?",
                    (code.upper(),)
                )
                
                # Записываем активацию
                cursor.execute(
                    "INSERT INTO promo_activations (tg_id, promo_code, requests_added) VALUES (?, ?, ?)",
                    (tg_id, code.upper(), requests)
                )
                
                conn.commit()
                return {'success': True, 'requests': requests}
                
        except Exception as e:
            print(f"❌ Ошибка при активации промокода: {e}")
            return {'success': False, 'message': 'Ошибка при активации промокода'}
    
    def get_all_promos(self):
        """Возвращает список всех промокодов"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT code, requests, max_uses, used, active FROM promo_codes ORDER BY created_at DESC"
                )
                promos = []
                for row in cursor.fetchall():
                    promos.append({
                        'code': row[0],
                        'requests': row[1],
                        'max_uses': row[2],
                        'used': row[3],
                        'active': bool(row[4])
                    })
                return promos
        except Exception as e:
            print(f"❌ Ошибка при получении списка промокодов: {e}")
            return []
    
    def delete_promo(self, code):
        """Удаляет промокод"""
        try:
            with self.lock, sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM promo_codes WHERE code = ?",
                    (code.upper(),)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    return True
                return False
        except Exception as e:
            print(f"❌ Ошибка при удалении промокода: {e}")
            return False

# Создаём глобальный экземпляр менеджера БД
db_manager = DatabaseManager()