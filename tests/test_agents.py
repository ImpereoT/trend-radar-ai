import os
from app.agents import save_md_report


def test_save_md_report_creates_file():
    """Тест проверяет, что файл отчета физически создается на диске"""
    topic = "Test Topic"
    content = "# Test Content"

    path = save_md_report(topic, content)

    # Проверяем, что файл существует
    assert os.path.exists(path)

    # Чистим за собой (необязательно, но полезно)
    if os.path.exists(path):
        os.remove(path)
