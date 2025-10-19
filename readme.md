# Телеграм-бот на основе API OpenAI

Телеграм-бот для взаимодействия с пользователями через API OpenAI.

## Особенности

- **Команда /start**: Приветствие пользователей и сохранение данных в базе данных
- **Команда /stats**: Просмотр статистики для администраторов (общее количество пользователей)
- **Обработка сообщений**: Генерация ответов с использованием OpenAI API
- **Индикатор "печатает..."**: Визуальная обратная связь во время обработки запроса
- **Минимальная длина сообщения**: Проверка на минимум 10 символов
- **SQLite база данных**: Хранение данных пользователей и истории взаимодействий

## Структура проекта

```
chatgpt-telegram-bot/
├── main.py          # Основной файл бота
├── functions.py     # Функции для работы с OpenAI API
├── db.py           # Управление базой данных
├── .env            # Конфигурационные переменные (создать вручную)
├── .env.example    # Шаблон для .env
├── requirements.txt
└── README.md
```

## Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/king-tri-ton/chatgpt-telegram-bot.git
   cd chatgpt-telegram-bot
   ```

2. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

3. **Создайте файл .env**
   
   Скопируйте `.env.example` и переименуйте в `.env`:
   ```bash
   cp .env.example .env
   ```

4. **Заполните переменные окружения в .env**
   ```
   AI_TOKEN=your_openai_api_token
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   ```

   - **AI_TOKEN**: Получите на [platform.openai.com](https://platform.openai.com/api-keys)
   - **BOT_TOKEN**: Получите у [@BotFather](https://t.me/botfather) в Telegram
   - **ADMIN_ID**: Ваш Telegram ID (узнать можно у [@username_to_id_bot](https://t.me/username_to_id_bot))

## Запуск

```bash
python bot.py
```

## Использование

1. Найдите вашего бота в Telegram
2. Отправьте `/start` для начала работы
3. Отправляйте сообщения (минимум 10 символов) для получения ответов от OpenAI
4. Администратор может использовать `/stats` для просмотра статистики

## Требования

- Python 3.7+
- Telegram аккаунт
- OpenAI API ключ
- Библиотеки из requirements.txt:
  - telebot
  - requests
  - python-dotenv

## Отказ от ответственности

Используйте бота ответственно в соответствии с правилами Telegram и OpenAI. Убедитесь, что соблюдаете лимиты API и политики использования обеих платформ.

---

Если у вас есть предложения или вопросы — пишите в Telegram: [@king_triton](https://t.me/king_triton).
Проект распространяется по лицензии [MIT](LICENSE).