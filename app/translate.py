import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM = "Ты опытный литературный переводчик. Переводи на русский близко по смыслу, кратко и естественно; без пафоса и штампов."

def translate_meaning(en_text:str) -> str:
    if not en_text.strip():
        return ""
    prompt = "Переведи (не дословно, а органично по смыслу):\n" + en_text.strip()
    # Если у тебя обновлённый SDK, замени на соответствующий вызов
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":prompt}],
        temperature=0.3
    )
    return resp["choices"][0]["message"]["content"].strip()
