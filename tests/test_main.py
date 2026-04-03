import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_research_endpoint():
    """Тест проверяет полный цикл через транспорт ASGI"""
    # Используем ASGITransport для совместимости с новыми версиями httpx
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/research", json={"topic": "Тестовый анализ трендов 2026"})

    # Проверка статуса
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    # Проверка структуры отчета
    assert len(data["content"]) > 100
    assert "1." in data["content"]

    # Проверка наличия ссылок на файлы
    assert "report_file" in data
    assert "chart_file" in data
