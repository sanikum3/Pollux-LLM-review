from groq import Groq
from analys import *
import json
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
def get_sections(name_xml='result.xml'):
    name = extract(name_xml)
    with open(name, "r", encoding="utf-8") as f:
        text = f.read()
    sections = text.split("\n")
    return sections
def compress_sections(name_xml='result.xml'):
    sections = get_sections(name_xml)
    compressed = []

    client = Groq(api_key=API_KEY)

    for sec in sections:
        if len(sec.strip()) < 50:
            continue

        prompt = f"""
Сократи текст раздела научной статьи.

СТРОГО:
- НЕ добавляй новых фактов
- НЕ интерпретируй
- НЕ обобщай
- Используй только формулировки из текста
- Можно удалять повторы и второстепенные детали

Верни краткий, фактологический пересказ.
Это фрагмент научной статьи.
Он может быть:
- введением
- определением
- теоретическим утверждением
- обсуждением

НЕ:
- классифицируй
- НЕ добавляй структуру
- НЕ делай выводы
Текст:
{sec}
"""
        r = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200
        )

        compressed.append(r.choices[0].message.content)

    return compressed


