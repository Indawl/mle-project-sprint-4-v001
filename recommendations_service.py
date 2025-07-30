import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from utils.recommendations import Recommendations
from utils.event_store import EventStore
from utils.utils import als_sim, items


# Используем логгер uvicorn для логирования всех сообщений
logger = logging.getLogger("uvicorn.error")

rec_store = Recommendations()
events_store = EventStore()


# Жизненный цикл приложения: загружаем данные при старте и освобождаем ресурсы при завершении
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Сервис запущен!")

    rec_store.load(
        type="personal",
        path="recsys/recommendations/personal_als.parquet",
        columns=["user_id", "item_id", "score"],
    )
    rec_store.load(
        type="default",
        path="recsys/recommendations/top_popular.parquet",
        columns=["item_id", "popularity_weighted"],
    )

    yield
    logger.info("Сервис остановлен!")


# Инициализация FastAPI
app = FastAPI(title="Микросервис по рекомендациям", lifespan=lifespan)


@app.post("/recommendations", name="Получить рекомендации по пользователю")
async def recommendations(user_id: int, k: int = 100):
    """
    Возвращает объединённые рекомендации (онлайн + офлайн) длиной k для пользователя
    """

    recs_offline = rec_store.get(user_id, k)

    recs_online = await get_online_rec(user_id, k, N=10)
    recs_online = recs_online["recs"]

    logger.info(f"Offline рекомендации: {recs_offline}")
    logger.info(f"Online рекомендации: {recs_online}")

    # Смешиваем рекомендации, чередуя офлайн и онлайн
    blended = [
        val
        for pair in zip(recs_online, recs_offline)
        for val in pair
    ]
    blended.extend(recs_online[len(recs_offline):])
    blended.extend(recs_offline[len(recs_online):])

    # Удаляем дубликаты, сохраняем порядок и ограничиваем длину
    recs_blended = list(dict.fromkeys(blended))[:k]

    # Отображаем названия и артистов по рекомендациям
    for item_id in recs_blended:
        try:
            row = items.loc[items["item_id"] == item_id]
            print("Трек:", row["item_name"].values[0])
            print("Исполнитель:", row["artist_name"].values[0])
        except IndexError:
            logger.warning(f"ID трека {item_id} не найден!")

    return {"recs": recs_blended}


@app.post("/get_online_rec", name="Получить Online рекомендации по пользователю")
async def get_online_rec(user_id: int, k: int = 100, N: int = 10):
    """
    Генерирует онлайн-рекомендации на основе последних действий пользователя
    """

    events = await get_user_events(user_id, k)
    events = events["events"]

    sim_ids, sim_scores = [], []
    for item_id in events:
        ids, scores = await als_sim(item_id, N)
        sim_ids.extend(ids)
        sim_scores.extend(scores)

    # Сортируем и убираем дубликаты
    combined = sorted(zip(sim_ids, sim_scores), key=lambda x: x[1], reverse=True)
    recs = list(dict.fromkeys([item_id for item_id, _ in combined]))

    for item_id in recs:
        try:
            row = items.loc[items["item_id"] == item_id]
            print("Трек:", row["item_name"].values[0])
            print("Исполнитель:", row["artist_name"].values[0])
        except IndexError:
            logger.warning(f"ID трека {item_id} не найден!")

    return {"recs": recs}


@app.post("/put_user_event")
async def put_user_event(user_id: int, item_id: int):
    """
    Сохраняет действие пользователя (прослушивание трека)
    """
    events_store.put(user_id, item_id)
    return {"result": "ok"}


@app.post("/get_user_events")
async def get_user_events(user_id: int, k: int = 10):
    """
    Возвращает последние k событий пользователя
    """
    return {"events": events_store.get(user_id, k)}


@app.get("/load_recommendations", name="Загрузить рекомендации")
async def load_recommendations(rec_type: str, file_path: str):
    """
    Позволяет вручную перезагрузить офлайн-рекомендации из указанного файла
    """
    columns = ["user_id", "item_id", "score"] if rec_type == "personal" else ["item_id", "popularity_weighted"]
    rec_store.load(type=rec_type, path=file_path, columns=columns)
    return {"result": "ok"}


@app.get("/get_statistics", name="Статистика использования рекомендаций")
async def get_statistics():
    """
    Возвращает статистику использования рекомендаций
    """
    return rec_store.stats()
