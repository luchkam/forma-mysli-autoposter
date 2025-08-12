from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = "Ты опытный литературный переводчик. Переводи на русский близко по смыслу, кратко и естественно; без пафоса и штампов."

def translate_meaning(en_text: str) -> str:
    if not en_text.strip():
        return ""
    
    prompt = "Переведи (не дословно, а органично по смыслу):\n" + en_text.strip()
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = resp.choices[0].message.content.strip()
        print("🔍 Перевод:", result)  # Лог для отладки
        return result
    except Exception as e:
        print("❌ Ошибка перевода:", e)
        return en_text  # Если перевод не удался — возвращаем английский
