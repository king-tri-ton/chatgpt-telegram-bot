from config import AI_TOKEN
import requests

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
    response = requests.post(url, json=data, headers=headers)

    return response.json()["choices"][0]["message"]["content"]