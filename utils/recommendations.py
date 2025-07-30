import pandas as pd
import logging


# Используем логгер uvicorn для логирования всех сообщений
logger = logging.getLogger("uvicorn.error")


class Recommendations:
    def __init__(self):
        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,    # счетчик персональных рекомендаций
            "request_default_count": 0,     # счетчик топ-рекомендаций
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла

        type == "personal" - персональные (при помощи ALS)
        type == "default" - топ-рекомендации
        """

        logger.info(f"Загрузка рекомендаций, тип: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)

        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")

        logger.info(f"Рекомендация успешно загружена!")

    def get(self, user_id: int, k: int = 100):
        """
        Возвращает список рекомендаций для пользователя
        """

        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
            logger.info(f"Найдено {len(recs)} персональных рекомендаций!")
        except:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
            logger.info(f"Найдено {len(recs)} TOP-рекомендаций!")

        if not recs:
            logger.error("Рекомендации не найдены!")
            recs = []

        return recs

    def stats(self):
        logger.info("Статистика использования рекомендаций:")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")
        print(self._stats)
        return self._stats
    