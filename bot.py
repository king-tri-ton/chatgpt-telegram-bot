from functions import get_openai_response
from config import BOT_TOKEN, ADMIN_ID
from db import db_manager
import telebot

# Создание экземпляра бота с использованием вашего токена
bot = telebot.TeleBot(BOT_TOKEN)

# Создание таблиц в базе данных
db_manager.create_tables()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Запись данных пользователя в базу данных
    db_manager.add_user(message.chat.id)
    bot.reply_to(message, "Привет! Я ваш дружелюбный бот в Telegram.")

# Обработчик команды /stats
@bot.message_handler(commands=['stats'])
def show_stats(message):
    # Проверка, является ли пользователь администратором
    if message.from_user.id == ADMIN_ID:
        # Получение количества пользователей из базы данных
        total_users = db_manager.get_total_users()
        bot.reply_to(message, f"Количество пользователей, воспользовавшихся ботом: {total_users}")
    else:
        bot.reply_to(message, "У вас нет прав на выполнение этой команды.")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def generate_result(message):
    # Проверка длины сообщения
    if len(message.text) < 10:
        bot.send_message(message.chat.id, "Введите сообщение длиной не менее 10 символов.")
        return

    response = get_openai_response(message.text)

    db_manager.add_result(message.chat.id, message.text, response)

    bot.reply_to(message, response)

    


# Запуск бота
bot.infinity_polling(interval=0)