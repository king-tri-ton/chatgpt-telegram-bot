import os
from dotenv import load_dotenv
import requests

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение AI_TOKEN из окружения
AI_TOKEN = os.getenv('AI_TOKEN')

# Проверка наличия токена
if not AI_TOKEN:
    raise ValueError("AI_TOKEN не найден в .env файле")

# Function to send a message to OpenAI's Chat Completions API and get a response
def get_openai_response(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Ошибка при обращении к OpenAI API: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Ошибка при обработке ответа от OpenAI: {str(e)}"