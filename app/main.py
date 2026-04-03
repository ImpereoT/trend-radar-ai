import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from app.agents import run_research

app = FastAPI(title="TrendRadar AI")


class ResearchRequest(BaseModel):
    topic: str


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Создаем папки
for folder in ["storage/charts", "storage/reports", "static"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

app.mount("/storage", StaticFiles(directory=os.path.join(BASE_DIR,
          "storage")), name="storage")
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
async def read_index():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    return FileResponse(index_path)


@app.post("/research")
async def perform_research(request: ResearchRequest):
    try:
        print(f"\n[HTTP] Получен запрос: {request.topic}")
        # Запускаем тяжелую логику в отдельном потоке
        result = await run_in_threadpool(run_research, request.topic)
        print(f"[HTTP] Ответ успешно отправлен на фронтенд")
        return result
    except Exception as e:
        print(f"[HTTP ERROR] Критическая ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
