import os
import json
import re
import time
from datetime import datetime
from langchain_openai import ChatOpenAI
from app.tools import web_search_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.visualizer import generate_trend_chart

# Настройки модели
llm = ChatOpenAI(
    model=settings.model_id,
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base,
    temperature=0.7,
    max_tokens=4000,
    timeout=150
)


def save_md_report(topic: str, content: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_topic = topic.replace(" ", "_").lower()[:30]
    filename = f"report_{safe_topic}_{timestamp}.md"
    full_path = os.path.join(settings.reports_dir, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"storage/reports/{filename}"


def run_research(topic: str):
    try:
        # --- ШАГ 1: ROUTER ---
        print(f"[*] [1/5] Определение стратегии...")
        router_prompt = ChatPromptTemplate.from_template(
            "Запрос: '{topic}'. Ответь одним словом: 'COMPARE' или 'SUMMARY'.")
        router_chain = router_prompt | llm | StrOutputParser()
        route_type = "".join(
            filter(str.isalpha, router_chain.invoke({"topic": topic}).upper()))

        print(f"    -> Выбрана стратегия: {route_type}")

        # --- ШАГ 2: RESEARCHER ---
        print(f"[*] [2/5] Сбор данных...")
        raw_data = web_search_tool.run(
            f"detailed technical analysis, market reports and forecast 2024-2030 with source URLs: {topic}")

        print(f"    -> Собрано данных: {len(raw_data)} символов")

        # --- ШАГ 3: ANALYST (Контент) ---
        print(f"[*] [3/5] Генерация аналитики...")
        analysis_template = """
        Ты ведущий аналитик. Напиши глубокий отчет по теме: {topic}
        Контекст: {data}
        
        СТРУКТУРА (ОБЯЗАТЕЛЬНО ВСЕ 5 ПУНКТОВ):
        1. 🌍 ГЛОБАЛЬНЫЙ МАКРО-КОНТЕКСТ (2024-2026)
        2. 🔍 ГЛУБОКИЙ ТЕХНИЧЕСКИЙ/СТРАТЕГИЧЕСКИЙ АНАЛИЗ
        3. 🚀 ТЕХНОЛОГИЧЕСКИЙ ФУНДАМЕНТ И R&D
        4. ⚠️ КРИТИЧЕСКИЕ РИСКИ И ПРОГНОЗ 2030
        5. 💡 СТРАТЕГИЧЕСКИЕ РЕКОМЕНДАЦИИ И ИСТОЧНИКИ
        
        ВАЖНО: Сохраняй все найденные URL-адреса источников.
        В самом конце текста напиши строку: 
        MARKER_DATA: 2024-(число), 2025-(число), 2026-(число)
        """
        analysis_prompt = ChatPromptTemplate.from_template(analysis_template)
        analysis_result = (analysis_prompt | llm | StrOutputParser()).invoke(
            {"topic": topic, "data": raw_data})

        # --- ШАГ 4: EXTRACTOR (Данные для графика) ---
        print(f"[*] [4/5] Извлечение данных тренда...")
        extract_prompt = ChatPromptTemplate.from_template(
            "Извлеки из текста 3 значения (для 2024, 2025, 2026 годов). "
            "Верни ТОЛЬКО чистый JSON формат {{'2024': 10, '2025': 20, '2026': 30}}. "
            "Текст: {text}"
        )
        chart_data_raw = (extract_prompt | llm | StrOutputParser()).invoke(
            {"text": analysis_result})

        chart_path = None
        try:
            clean_json_str = re.search(
                r"\{.*\}", chart_data_raw.replace("\n", ""), re.DOTALL).group()
            chart_data = json.loads(clean_json_str.replace("'", '"'))
            chart_path = generate_trend_chart(topic, chart_data)
            print(f"    -> График создан: {chart_path}")
        except Exception as e:
            print(f"    [!] Ошибка экстрактора данных: {e}")

        # --- ШАГ 5: EDITOR (Оформление и ссылки) ---
        print(f"[*] [5/5] Финальная верстка...")
        editor_prompt = ChatPromptTemplate.from_template(
            "Ты редактор Forbes. Оформи этот текст профессионально. "
            "1. Используй H1, H2, эмодзи и жирный шрифт. "
            "2. КРИТИЧЕСКИ ВАЖНО: Преврати все упоминания источников и URL в активные Markdown-ссылки [Название/Источник](URL). "
            "3. Убедись, что раздел 'ИСТОЧНИКИ' содержит список кликабельных ссылок. "
            "4. Удали технический маркер MARKER_DATA. \n\n"
            "ТЕКСТ: {analysis}"
        )
        final_text = (editor_prompt | llm | StrOutputParser()
                      ).invoke({"analysis": analysis_result})

        report_rel_path = save_md_report(topic, final_text)

        return {
            "status": "success",
            "content": final_text,
            "chart_file": chart_path,
            "report_file": report_rel_path
        }

    except Exception as e:
        print(f"[!!!] Критическая ошибка: {e}")
        raise e
