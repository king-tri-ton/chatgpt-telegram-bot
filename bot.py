import os
from dotenv import load_dotenv
from functions import get_openai_response
from db import db_manager
import telebot

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден в .env файле")

bot = telebot.TeleBot(BOT_TOKEN)
db_manager.create_tables()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    db_manager.add_user(message.chat.id)
    bot.reply_to(message, "Привет! Я ваш дружелюбный бот в Telegram.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        total_users = db_manager.get_total_users()
        bot.reply_to(message, f"Количество пользователей, воспользовавшихся ботом: {total_users}")
    else:
        bot.reply_to(message, "У вас нет прав на выполнение этой команды.")

@bot.message_handler(func=lambda message: True)
def generate_result(message):
    if len(message.text) < 10:
        bot.send_message(message.chat.id, "Введите сообщение длиной не менее 10 символов.")
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    response = get_openai_response(message.text)
    db_manager.add_result(message.chat.id, message.text, response)
    bot.reply_to(message, response)

if __name__ == '__main__':
    bot.infinity_polling(interval=0)