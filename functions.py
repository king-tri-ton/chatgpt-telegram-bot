from config import AI_TOKEN
from openai import OpenAI

if not AI_TOKEN:
    raise ValueError("AI_TOKEN не найден в .env файле")

# Создаём клиента OpenAI
client = OpenAI(api_key=AI_TOKEN)

def get_openai_response(message: str, effort: str = "low", verbosity: str = "low"):
    """
    Получает ответ от GPT-5 через новый Responses API.
    Возвращает текст ответа и метаданные (prompt_tokens, completion_tokens).
    """
    try:
        result = client.responses.create(
            model="gpt-5",
            input=message,
            reasoning={"effort": effort},
            text={"verbosity": verbosity},
        )

        text = result.output_text
        usage = getattr(result, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", 0)
        completion_tokens = getattr(usage, "output_tokens", 0)
        
        return text, prompt_tokens, completion_tokens
        
    except Exception as e:
        print(f"❌ ОШИБКА в get_openai_response: {e}")
        import traceback
        traceback.print_exc()
        return f"Ошибка при обращении к GPT-5 API: {e}", 0, 0