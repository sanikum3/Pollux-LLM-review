from groq import Groq
import json
from dotenv import load_dotenv
import os

from analys import analyze, build_input
from compress import get_sections, compress_sections

load_dotenv()

TOKEN = os.getenv("GROQ_API_KEY")

def run_llm(payload_json: str) -> str:
    client = Groq(api_key=TOKEN)
    prompt = f"""
Пиши ответ СТРОГО в Markdown.

ФОРМАТ ОБЯЗАТЕЛЕН:
## 1. Новизна
## 2. Актуальность
## 3. Сильные стороны
## 4. Слабые стороны
## 5. Рекомендации авторам
## 6. Итоговая оценка

ТРЕБОВАНИЯ:
- Используй ТОЛЬКО факты из текста
- Не добавляй внешние знания
- Если статья обзорная или классическая —
  оценивай новизну и актуальность ТОЛЬКО в рамках статьи

ВХОДНЫЕ ДАННЫЕ:
{payload_json}
"""

    r = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=900
    )

    return r.choices[0].message.content


# =========================
# FACT EXTRACTION
# =========================

def extract_facts(payload_json: str) -> str:
    client = Groq(api_key=TOKEN)
    prompt = f"""
Извлеки ТОЛЬКО ФАКТЫ из статьи.

Верни JSON:
- contributions
- methods
- datasets
- results
- limitations
- core_claims
- key_concepts
- theoretical_results
- assumptions
- stated_limitations

Если пункта нет — верни [].
ЗАПРЕЩЕНО добавлять что-либо от себя.

ТЕКСТ:
{payload_json}
"""

    r = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600
    )

    return r.choices[0].message.content


# =========================
# CRITIC (ВНУТРЕННИЙ)
# =========================

def critic(review: str, facts: str) -> str:
    client = Groq(api_key=TOKEN)
    prompt = f"""
Ты — внутренний проверяющий.

ФАКТЫ:
{facts}

РЕЦЕНЗИЯ:
{review}

Найди:
- UNSUPPORTED_CLAIMS
- DISTORTIONS
- OVERGENERALIZATIONS

Это ВНУТРЕННИЙ ОТЧЁТ.
НЕ ПЕРЕПИСЫВАЙ РЕЦЕНЗИЮ.
"""

    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1200
    )

    return r.choices[0].message.content


# =========================
# PIPELINE
# =========================
def get_review(inp):
    #inp = input()
    client = Groq(api_key=TOKEN)
    analysis_result = analyze(inp)
    raw_sections = get_sections("result.xml")
    compressed_sections = compress_sections("result.xml")

    payload_compressed = build_input(compressed_sections, analysis_result[0])
    payload_raw = build_input(raw_sections, analysis_result[0])

    generated_review = run_llm(payload_compressed)
    facts = extract_facts(payload_raw)
    critique = critic(generated_review, facts)

    final_review = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
    Ты — редактор научных рецензий.
    Пиши СТРОГО в Markdown.
    ТВОЯ ЗАДАЧА:
    - Переписать рецензию с учётом critic report
    - Вернуть ТОЛЬКО итоговую рецензию БЕЗ РЕЗКИХ ПРЕРЫВАНИЙ

    СТРОГИЙ ФОРМАТ:
    ## 1. Новизна
    ## 2. Актуальность
    ## 3. Сильные стороны
    ## 4. Слабые стороны
    ## 5. Рекомендации авторам
    ## 6. Итоговая оценка (плохо/средне/принято)

    ЗАПРЕЩЕНО:
    - упоминать critic
    - упоминать ошибки
    - писать "следует", "нужно исправить"
    - добавлять новые факты

    Пиши СТРОГО в Markdown.
    """
            },
            {
                "role": "user",
                "content": f"""
    ОРИГИНАЛЬНАЯ РЕЦЕНЗИЯ:
    {generated_review}

    ВНУТРЕННИЙ ОТЧЁТ (НЕ ВКЛЮЧАТЬ В ВЫВОД):
    {critique}
    """
            }
        ],
        temperature=0.25,
        max_tokens=1200
    ).choices[0].message.content


    # =========================
    # SAVE
    # =========================

    with open("final_review.md", "w", encoding="utf-8") as f:
        f.write(final_review)

    print("Final review saved to final_review.md")
    return "final_review.md"  


