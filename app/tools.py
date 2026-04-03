from langchain_core.tools import Tool
from ddgs import DDGS


def web_search_func(query: str) -> str:
    results = []
    try:
        # Добавляем таймаут и эмуляцию браузера через заголовки
        with DDGS(timeout=20) as ddgs:
            # Используем генератор и ловим результаты
            res = ddgs.text(query, max_results=8)
            for r in res:
                results.append(
                    f"Title: {r['title']}\nSource: {r['href']}\nSnippet: {r['body']}")
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return "Ничего не найдено."

    return "\n---\n".join(results) if results else "Ничего не найдено."


web_search_tool = Tool(
    name="WebSearch",
    func=web_search_func,
    description="Поиск актуальных новостей."
)
