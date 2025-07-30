import requests
import logging


logging.basicConfig(
    filename="test_service.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

def log_response(resp):
    if resp.status_code == 200:
        return resp.json()
    else:
        logging.info(f"!!!ERROR!!! Status code: {resp.status_code}")
        return []

headers = {"Content-type": "application/json", "Accept": "text/plain"}
user_id = 57

recommendations_url = "http://127.0.0.1:8000/recommendations"
params = {"user_id": user_id}
recs = log_response(requests.post(recommendations_url, headers=headers, params=params))
logging.info(f"Полученные идентификаторы рекомендаций для пользователя {user_id}: {recs}")

user_id2 = 345722346344
params = {"user_id": user_id2}
recs = log_response(requests.post(recommendations_url, headers=headers, params=params))
logging.info(f"Полученные идентификаторы рекомендаций для пользователя {user_id2} без персональных рекомендаций (с топ-рекомендациями): {recs}")

load_recommendations_url = "http://127.0.0.1:8000/load_recommendations"
params = {"rec_type": "default", "file_path": "recsys/recommendations/top_popular.parquet"}
req = requests.get(load_recommendations_url, headers=headers, params=params)
logging.info(f"Загрузка рекомендаций: Status code: {req.status_code}")

get_statistics_url = "http://127.0.0.1:8000/get_statistics"
recs = log_response(requests.get(get_statistics_url))
logging.info(f"Статистика рекомендаций: {recs}")

get_user_events_url = "http://127.0.0.1:8000/get_user_events"
params = {"user_id": user_id, "k": 10}
recs = log_response(requests.post(get_user_events_url, headers=headers, params=params))
logging.info(f"События пользователя {user_id}: {recs}")

put_user_events_url = 'http://127.0.0.1:8000/put_user_event'
for i in [26, 38, 135, 136, 138]:
    params = {"user_id": user_id, "item_id": i}
    recs = log_response(requests.post(put_user_events_url, headers=headers, params=params))
    logging.info(f"Произошло событие {i} для пользователя {user_id}: {recs}")

params = {"user_id": user_id, "k": 10}
recs = log_response(requests.post(get_user_events_url, headers=headers, params=params))
logging.info(f"События пользователя {user_id}: {recs}")

get_online_rec_url = 'http://127.0.0.1:8000/get_online_rec'
params = {"user_id": user_id, "k": 100, "N": 10}
recs = log_response(requests.post(get_online_rec_url, headers=headers, params=params))
logging.info(f"Онлайн-рекомендации для пользователя {user_id}: {recs}")

params = {"user_id": user_id}
recs = log_response(requests.post(recommendations_url, headers=headers, params=params))
logging.info(f"Полученные идентификаторы рекомендаций для пользователя {user_id}: {recs}")

get_statistics_url = "http://127.0.0.1:8000/get_statistics"
recs = log_response(requests.get(get_statistics_url))
logging.info(f"Статистика рекомендаций: {recs}")