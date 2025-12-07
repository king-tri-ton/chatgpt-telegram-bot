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

# Словари для хранения временных данных
waiting_for_amount = {}
waiting_for_user_id = {}
waiting_for_promo_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    db_manager.add_user(message.chat.id, initial_requests=3)
    requests = db_manager.get_user_requests(message.chat.id)
    
    welcome_text = (
        "👋 Привет! Я ваш AI-ассистент на базе GPT-5.1 Instant.\n\n"
        f"💰 Ваш баланс: {requests} запросов\n\n"
        "Просто напишите мне сообщение (минимум 10 символов), "
        "и я постараюсь помочь!\n\n"
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "/balance - проверить баланс\n"
        "/buy - купить запросы\n"
        "/promo - активировать промокод\n"
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
        "• Первые 3 запроса - бесплатно\n"
        "• Далее: 1 запрос = 1 ⭐ Telegram Star\n"
        "• Можно купить от 1 до 100 запросов\n"
        "• Или активировать промокод командой /promo\n\n"
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
        balance_text += "\n\n❌ Запросы закончились! Используйте /buy чтобы купить ещё или /promo для активации промокода."
    
    bot.reply_to(message, balance_text)

@bot.message_handler(commands=['promo'])
def activate_promo(message):
    bot.send_message(
        message.chat.id,
        "🎟️ Введите промокод:"
    )
    bot.register_next_step_handler(message, process_promo_code)

def process_promo_code(message):
    promo_code = message.text.strip().upper()
    
    result = db_manager.activate_promo(message.chat.id, promo_code)
    
    if result['success']:
        requests = db_manager.get_user_requests(message.chat.id)
        success_text = (
            f"✅ Промокод активирован!\n\n"
            f"➕ Добавлено запросов: {result['requests']}\n"
            f"💰 Ваш новый баланс: {requests} запросов"
        )
        bot.send_message(message.chat.id, success_text)
    else:
        bot.send_message(message.chat.id, f"❌ {result['message']}")

@bot.message_handler(commands=['dev'])
def show_dev_info(message):
    dev_text = (
        "👨‍💻 О разработчике и проекте\n\n"
        "🔹 Разработчик: King Triton\n"
        "🔹 Лицензия: MIT (Open Source)\n"
        "🔹 GitHub: https://github.com/king-tri-ton/chatgpt-telegram-bot\n\n"
        "💡 Идея проекта:\n"
        "Предоставить минимальный доступ к GPT-5.1 за символическую плату. "
        "1 Telegram Star за одно сообщение — это намного выгоднее, чем подписка на ChatGPT за $20!\n\n"
        "🌟 Преимущества:\n"
        "• Платите только за то, что используете\n"
        "• Нет ежемесячной подписки\n"
        "• Доступ к последней модели GPT-5.1\n"
        "• Удобство использования в Telegram\n\n"
        "⭐ Если вам понравился проект, поставьте звезду на GitHub!"
    )
    bot.reply_to(message, dev_text, disable_web_page_preview=True)

@bot.message_handler(commands=['buy'])
def buy_requests(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    buttons = [
        types.InlineKeyboardButton("1 ⭐", callback_data="buy_1"),
        types.InlineKeyboardButton("5 ⭐", callback_data="buy_5"),
        types.InlineKeyboardButton("10 ⭐", callback_data="buy_10"),
        types.InlineKeyboardButton("25 ⭐", callback_data="buy_25"),
        types.InlineKeyboardButton("50 ⭐", callback_data="buy_50"),
        types.InlineKeyboardButton("100 ⭐", callback_data="buy_100"),
    ]
    markup.add(*buttons)
    
    custom_button = types.InlineKeyboardButton("✏️ Своя сумма", callback_data="buy_custom")
    markup.add(custom_button)
    
    buy_text = (
        "💳 Покупка запросов\n\n"
        "Выберите количество запросов:\n"
        "1 запрос = 1 ⭐ Telegram Star\n\n"
        "Или введите свою сумму (от 1 до 100)"
    )
    
    bot.send_message(message.chat.id, buy_text, reply_markup=markup)

# ==================== АДМИНСКИЕ КОМАНДЫ ====================

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
    admin_text = (
        "👑 Панель администратора\n\n"
        "/stat - статистика бота\n"
        "/give - начислить запросы пользователю\n"
        "/createpromo - создать промокод\n"
        "/listpromo - список промокодов\n"
        "/deletepromo - удалить промокод"
    )
    bot.reply_to(message, admin_text)

@bot.message_handler(commands=['stat'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
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

@bot.message_handler(commands=['give'])
def give_requests_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
    bot.send_message(
        message.chat.id,
        "👤 Введите Telegram ID пользователя:"
    )
    bot.register_next_step_handler(message, process_give_user_id)

def process_give_user_id(message):
    try:
        user_id = int(message.text.strip())
        waiting_for_user_id[message.from_user.id] = user_id
        
        bot.send_message(
            message.chat.id,
            f"💰 Введите количество запросов для начисления пользователю {user_id}:"
        )
        bot.register_next_step_handler(message, process_give_amount)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ID. Попробуйте снова: /give")

def process_give_amount(message):
    try:
        amount = int(message.text.strip())
        user_id = waiting_for_user_id.get(message.from_user.id)
        
        if not user_id:
            bot.send_message(message.chat.id, "❌ Ошибка. Начните снова: /give")
            return
        
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Количество должно быть положительным числом.")
            return
        
        # Начисляем запросы
        if db_manager.add_requests(user_id, amount):
            del waiting_for_user_id[message.from_user.id]
            
            requests = db_manager.get_user_requests(user_id)
            bot.send_message(
                message.chat.id,
                f"✅ Пользователю {user_id} начислено {amount} запросов.\n"
                f"💰 Его новый баланс: {requests} запросов"
            )
            
            # Уведомляем пользователя
            try:
                bot.send_message(
                    user_id,
                    f"🎁 Вам начислено {amount} запросов от администратора!\n"
                    f"💰 Ваш новый баланс: {requests} запросов"
                )
            except:
                pass
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при начислении запросов.")
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат количества. Попробуйте снова: /give")

@bot.message_handler(commands=['createpromo'])
def create_promo_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
    bot.send_message(
        message.chat.id,
        "🎟️ Введите промокод (латиница, цифры, без пробелов):"
    )
    bot.register_next_step_handler(message, process_promo_name)

def process_promo_name(message):
    promo_code = message.text.strip().upper()
    
    if not promo_code.replace('_', '').replace('-', '').isalnum():
        bot.send_message(message.chat.id, "❌ Промокод может содержать только буквы, цифры, _ и -")
        return
    
    waiting_for_promo_data[message.from_user.id] = {'code': promo_code}
    
    bot.send_message(
        message.chat.id,
        "💰 Введите количество запросов, которое дает промокод:"
    )
    bot.register_next_step_handler(message, process_promo_requests)

def process_promo_requests(message):
    try:
        requests = int(message.text.strip())
        
        if requests <= 0:
            bot.send_message(message.chat.id, "❌ Количество должно быть положительным числом.")
            return
        
        promo_data = waiting_for_promo_data.get(message.from_user.id)
        if not promo_data:
            bot.send_message(message.chat.id, "❌ Ошибка. Начните снова: /createpromo")
            return
        
        promo_data['requests'] = requests
        
        bot.send_message(
            message.chat.id,
            "🔢 Введите максимальное количество использований (0 = без ограничений):"
        )
        bot.register_next_step_handler(message, process_promo_max_uses)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат. Введите число.")

def process_promo_max_uses(message):
    try:
        max_uses = int(message.text.strip())
        
        if max_uses < 0:
            bot.send_message(message.chat.id, "❌ Количество не может быть отрицательным.")
            return
        
        promo_data = waiting_for_promo_data.get(message.from_user.id)
        if not promo_data:
            bot.send_message(message.chat.id, "❌ Ошибка. Начните снова: /createpromo")
            return
        
        # Создаем промокод
        result = db_manager.create_promo(
            promo_data['code'],
            promo_data['requests'],
            max_uses if max_uses > 0 else None
        )
        
        del waiting_for_promo_data[message.from_user.id]
        
        if result:
            promo_text = (
                f"✅ Промокод создан!\n\n"
                f"🎟️ Код: {promo_data['code']}\n"
                f"💰 Запросов: {promo_data['requests']}\n"
                f"🔢 Использований: {max_uses if max_uses > 0 else '∞'}"
            )
            bot.send_message(message.chat.id, promo_text)
        else:
            bot.send_message(message.chat.id, "❌ Промокод с таким названием уже существует.")
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат. Введите число.")

@bot.message_handler(commands=['listpromo'])
def list_promos(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
    promos = db_manager.get_all_promos()
    
    if not promos:
        bot.send_message(message.chat.id, "📋 Промокодов пока нет.")
        return
    
    promo_text = "📋 Список промокодов:\n\n"
    
    for promo in promos:
        status = "✅ Активен" if promo['active'] else "❌ Деактивирован"
        max_uses = promo['max_uses'] if promo['max_uses'] else "∞"
        
        promo_text += (
            f"🎟️ {promo['code']}\n"
            f"   💰 Запросов: {promo['requests']}\n"
            f"   🔢 Использовано: {promo['used']}/{max_uses}\n"
            f"   {status}\n\n"
        )
    
    bot.send_message(message.chat.id, promo_text)

@bot.message_handler(commands=['deletepromo'])
def delete_promo_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав на выполнение этой команды.")
        return
    
    bot.send_message(
        message.chat.id,
        "🗑️ Введите промокод для удаления:"
    )
    bot.register_next_step_handler(message, process_delete_promo)

def process_delete_promo(message):
    promo_code = message.text.strip().upper()
    
    if db_manager.delete_promo(promo_code):
        bot.send_message(message.chat.id, f"✅ Промокод {promo_code} удален.")
    else:
        bot.send_message(message.chat.id, f"❌ Промокод {promo_code} не найден.")

# ==================== ОБРАБОТЧИКИ ПОКУПКИ ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_buy(call):
    try:
        if call.data == 'buy_custom':
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
        
        create_invoice(call.message.chat.id, call.from_user.id, amount)
        bot.answer_callback_query(call.id, f"✅ Счёт на {amount} ⭐ создан!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании инвойса: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при создании счёта")

def create_invoice(chat_id, user_id, amount):
    prices = [types.LabeledPrice(label=f"{amount} запросов", amount=amount)]
    
    bot.send_invoice(
        chat_id=chat_id,
        title=f"Покупка {amount} запросов",
        description=f"Вы покупаете {amount} запросов к GPT-5.1 боту",
        invoice_payload=f"requests_{amount}_{user_id}",
        provider_token="",
        currency="XTR",
        prices=prices
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payment_info = message.successful_payment
    
    payload_parts = payment_info.invoice_payload.split('_')
    amount = int(payload_parts[1])
    user_id = int(payload_parts[2])
    
    db_manager.add_requests(user_id, amount)
    
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

# ==================== ОСНОВНОЙ ОБРАБОТЧИК ====================

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
            
            del waiting_for_amount[message.from_user.id]
            create_invoice(message.chat.id, message.from_user.id, amount)
            
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите число от 1 до 100:"
            )
        return
    
    if len(message.text) < 10:
        bot.send_message(
            message.chat.id, 
            "⚠️ Пожалуйста, введите сообщение длиной не менее 10 символов."
        )
        return
    
    if len(message.text) > 4000:
        bot.send_message(
            message.chat.id,
            "⚠️ Сообщение слишком длинное. Максимум 4000 символов."
        )
        return
    
    requests = db_manager.get_user_requests(message.chat.id)
    
    if requests <= 0:
        no_requests_text = (
            "❌ У вас закончились запросы!\n\n"
            "Используйте /buy чтобы купить запросы или /promo для активации промокода.\n"
            "1 запрос = 1 ⭐ Telegram Star"
        )
        bot.send_message(message.chat.id, no_requests_text)
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response_text, prompt_tokens, completion_tokens = get_openai_response(message.text)
        
        if db_manager.use_request(message.chat.id):
            db_manager.add_result(
                message.chat.id, 
                message.text, 
                response_text,
                prompt_tokens,
                completion_tokens
            )
            
            requests = db_manager.get_user_requests(message.chat.id)
            
            bot.reply_to(message, response_text, parse_mode='HTML')
            
            if requests > 0:
                balance_info = f"💰 Осталось запросов: {requests}"
                bot.send_message(message.chat.id, balance_info)
            else:
                bot.send_message(
                    message.chat.id,
                    "❌ У вас закончились запросы! Используйте /buy чтобы купить ещё или /promo для активации промокода."
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