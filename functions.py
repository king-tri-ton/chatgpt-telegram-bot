from config import AI_TOKEN, SYSTEM_PROMPT
from openai import OpenAI
import re
import html

if not AI_TOKEN:
    raise ValueError("AI_TOKEN не найден в .env файле")


client = OpenAI(api_key=AI_TOKEN)

def md_to_html(md: str) -> str:
    md = html.escape(md)

    # Распознаём код-блоки ```lang ... ```
    def block_code(match):
        code = match.group(2)
        return f"<pre><code>{code}</code></pre>"

    md = re.sub(r"```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```", block_code, md)

    # inline code `...`
    md = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", md)

    # Жирный **...**
    md = re.sub(r"\*\*(.*?)\*\*", lambda m: f"<b>{m.group(1)}</b>", md)

    # Курсив *...*
    md = re.sub(r"\*(.*?)\*", lambda m: f"<i>{m.group(1)}</i>", md)

    # Заголовки # text → просто <b>text</b>
    md = re.sub(r"^#+\s*(.*)$", lambda m: f"<b>{m.group(1)}</b>", md, flags=re.MULTILINE)

    # Цитаты "> ..."
    md = re.sub(r"^&gt;\s?(.*)$", r"<blockquote>\1</blockquote>", md, flags=re.MULTILINE)

    # Переводы строк
    md = md.replace("\n", "\n")

    return md

def get_openai_response(message: str, effort: str = "low", verbosity: str = "low"):
    """
    Получает ответ от GPT-5.1 через новый Responses API.
    Возвращает текст ответа и метаданные (prompt_tokens, completion_tokens).
    """
    try:
        result = client.responses.create(
            model="gpt-5.1",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            reasoning={"effort": effort},
            text={"verbosity": verbosity},
        )

        text = result.output_text
        usage = getattr(result, "usage", None)
        prompt_tokens = getattr(usage, "input_tokens", 0)
        completion_tokens = getattr(usage, "output_tokens", 0)
        text = md_to_html(text)
        return text, prompt_tokens, completion_tokens
        
    except Exception as e:
        print(f"ОШИБКА в get_openai_response: {e}")
        import traceback
        traceback.print_exc()
        return f"Ошибка при обращении к GPT-5.1 API: {e}", 0, 0
