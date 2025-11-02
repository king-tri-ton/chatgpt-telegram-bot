from config import BOT_TOKEN, ADMIN_ID
from functions import get_openai_response
from db import db_manager
import telebot
from telebot import types

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден в .env файле")

bot = telebot.TeleBot(BOT_TOKEN)

# Создаём таблицы при запуске
db_manager.create_tables()

# Словарь для хранения временных данных о пользователях, ожидающих ввода суммы
waiting_for_amount = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    db_manager.add_user(message.chat.id, initial_requests=1)
    requests = db_manager.get_user_requests(message.chat.id)
    
    welcome_text = (
        "👋 Привет! Я ваш AI-ассистент на базе GPT-5.\n\n"
        f"💰 Ваш баланс: {requests} запросов\n\n"
        "Просто напишите мне сообщение (минимум 10 символов), "
        "и я постараюсь помочь!\n\n"
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "/balance - проверить баланс\n"
        "/buy - купить запросы\n"
        "/dev - о разработчике и проекте"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "ℹ️ Как пользоваться ботом:\n\n"
        "1. Напишите мне любой вопрос или запрос\n"
        "2. Сообщение должно быть не короче 10 символов\n"
        "3. Получите ответ\n\n"
        "💰 Стоимость:\n"
        "• Первый запрос - бесплатно\n"
        "• Далее: 1 запрос = 1 ⭐ Telegram Star\n"
        "• Можно купить от 1 до 100 запросов\n\n"
        "Примеры запросов:\n"
        "• Объясни квантовую физику простыми словами\n"
        "• Напиши стихотворение про осень\n"
        "• Помоги с решением задачи по математике"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['balance'])
def check_balance(message):
    requests = db_manager.get_user_requests(message.chat.id)
    
    balance_text = f"💰 Ваш баланс: {requests} запросов"
    
    if requests == 0:
        balance_text += "\n\n❌ Запросы закончились! Используйте /buy чтобы купить ещё."
    
    bot.reply_to(message, balance_text)

@bot.message_handler(commands=['dev'])
def show_dev_info(message):
    dev_text = (
        "👨‍💻 О разработчике и проекте\n\n"
        "🔹 Разработчик: King Triton\n"
        "🔹 Лицензия: MIT (Open Source)\n"
        "🔹 GitHub: https://github.com/king-tri-ton/chatgpt-telegram-bot\n\n"
        "💡 Идея проекта:\n"
        "Предоставить минимальный доступ к GPT-5 за символическую плату. "
        "1 Telegram Star за одно сообщение — это намного выгоднее, чем подписка на ChatGPT за $20!\n\n"
        "🌟 Преимущества:\n"
        "• Платите только за то, что используете\n"
        "• Нет ежемесячной подписки\n"
        "• Доступ к последней модели GPT-5\n"
        "• Удобство использования в Telegram\n\n"
        "⭐ Если вам понравился проект, поставьте звезду на GitHub!"
    )
    bot.reply_to(message, dev_text, disable_web_page_preview=True)

@bot.message_handler(commands=['buy'])
def buy_requests(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Популярные варианты
    buttons = [
        types.InlineKeyboardButton("1 ⭐", callback_data="buy_1"),
        types.InlineKeyboardButton("5 ⭐", callback_data="buy_5"),
        types.InlineKeyboardButton("10 ⭐", callback_data="buy_10"),
        types.InlineKeyboardButton("25 ⭐", callback_data="buy_25"),
        types.InlineKeyboardButton("50 ⭐", callback_data="buy_50"),
        types.InlineKeyboardButton("100 ⭐", callback_data="buy_100"),
    ]
    markup.add(*buttons)
    
    # Кнопка для произвольной суммы
    custom_button = types.InlineKeyboardButton("✏️ Своя сумма", callback_data="buy_custom")
    markup.add(custom_button)
    
    buy_text = (
        "💳 Покупка запросов\n\n"
        "Выберите количество запросов:\n"
        "1 запрос = 1 ⭐ Telegram Star\n\n"
        "Или введите свою сумму (от 1 до 100)"
    )
    
    bot.send_message(message.chat.id, buy_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_buy(call):
    try:
        if call.data == 'buy_custom':
            # Запрашиваем произвольную сумму
            waiting_for_amount[call.from_user.id] = True
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                "✏️ Введите количество запросов (от 1 до 100):"
            )
            return
        
        amount = int(call.data.split('_')[1])
        
        if amount < 1 or amount > 100:
            bot.answer_callback_query(call.id, "❌ Неверное количество!")
            return
        
        # Создаём инвойс
        create_invoice(call.message.chat.id, call.from_user.id, amount)
        bot.answer_callback_query(call.id, f"✅ Счёт на {amount} ⭐ создан!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании инвойса: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при создании счёта")

def create_invoice(chat_id, user_id, amount):
    """Создаёт инвойс для оплаты"""
    prices = [types.LabeledPrice(label=f"{amount} запросов", amount=amount)]
    
    bot.send_invoice(
        chat_id=chat_id,
        title=f"Покупка {amount} запросов",
        description=f"Вы покупаете {amount} запросов к GPT-5 боту",
        invoice_payload=f"requests_{amount}_{user_id}",
        provider_token="",  # Для Telegram Stars не нужен
        currency="XTR",  # Telegram Stars
        prices=prices
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    """Подтверждаем оплату"""
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    """Обрабатываем успешную оплату"""
    payment_info = message.successful_payment
    
    # Парсим payload
    payload_parts = payment_info.invoice_payload.split('_')
    amount = int(payload_parts[1])
    user_id = int(payload_parts[2])
    
    # Добавляем запросы пользователю
    db_manager.add_requests(user_id, amount)
    
    # Сохраняем информацию о платеже
    db_manager.add_payment(
        tg_id=user_id,
        amount=amount,
        stars_paid=amount,
        payment_id=payment_info.telegram_payment_charge_id
    )
    
    requests = db_manager.get_user_requests(user_id)
    
    success_text = (
        f"✅ Оплата прошла успешно!\n\n"
        f"➕ Добавлено запросов: {amount}\n\n"
        f"💰 Ваш новый баланс: {requests} запросов"
    )
    
    bot.send_message(message.chat.id, success_text)

@bot.message_handler(commands=['stat'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        total_users = db_manager.get_total_users()
        total_requests = db_manager.get_total_requests()
        total_revenue = db_manager.get_total_revenue()
        
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"💬 Всего запросов: {total_requests}\n"
            f"⭐ Выручка: {total_revenue} звёзд"
        )
        bot.reply_to(message, stats_text)
    else:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")

@bot.message_handler(func=lambda message: True)
def generate_result(message):
    # Проверяем, ожидается ли ввод суммы для покупки
    if message.from_user.id in waiting_for_amount:
        try:
            amount = int(message.text.strip())
            
            if amount < 1 or amount > 100:
                bot.send_message(
                    message.chat.id,
                    "❌ Неверная сумма! Введите число от 1 до 100:"
                )
                return
            
            # Удаляем из словаря ожидания
            del waiting_for_amount[message.from_user.id]
            
            # Создаём инвойс
            create_invoice(message.chat.id, message.from_user.id, amount)
            
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите число от 1 до 100:"
            )
        return
    
    # Проверка минимальной длины сообщения
    if len(message.text) < 10:
        bot.send_message(
            message.chat.id, 
            "⚠️ Пожалуйста, введите сообщение длиной не менее 10 символов."
        )
        return
    
    # Проверка максимальной длины
    if len(message.text) > 4000:
        bot.send_message(
            message.chat.id,
            "⚠️ Сообщение слишком длинное. Максимум 4000 символов."
        )
        return
    
    # Проверяем баланс запросов
    requests = db_manager.get_user_requests(message.chat.id)
    
    if requests <= 0:
        no_requests_text = (
            "❌ У вас закончились запросы!\n\n"
            "Используйте команду /buy чтобы купить запросы.\n"
            "1 запрос = 1 ⭐ Telegram Star"
        )
        bot.send_message(message.chat.id, no_requests_text)
        return
    
    # Показываем, что бот печатает
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Получаем ответ от GPT-5
        response_text, prompt_tokens, completion_tokens = get_openai_response(message.text)
        
        # Используем один запрос
        if db_manager.use_request(message.chat.id):
            # Сохраняем в БД
            db_manager.add_result(
                message.chat.id, 
                message.text, 
                response_text,
                prompt_tokens,
                completion_tokens
            )
            
            # Получаем обновлённый баланс
            requests = db_manager.get_user_requests(message.chat.id)
            
            # Отправляем ответ пользователю
            bot.reply_to(message, response_text)
            
            # Показываем остаток запросов
            if requests > 0:
                balance_info = f"💰 Осталось запросов: {requests}"
                bot.send_message(message.chat.id, balance_info)
            else:
                bot.send_message(
                    message.chat.id,
                    "❌ У вас закончились запросы! Используйте /buy чтобы купить ещё."
                )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при использовании запроса")
        
    except Exception as e:
        error_message = f"❌ Произошла ошибка: {str(e)}"
        bot.reply_to(message, error_message)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    bot.infinity_polling(interval=0)