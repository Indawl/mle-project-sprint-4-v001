# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/Indawl/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится файлы с данными и моделью.

Скачайте их из S3_BUCKET командой:

```
python recsys/load_data.py
```

Также необходимо создать файл `.env` по шаблону `.env.template` и заполнить его

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Запустить сервис можно командой:

```
uvicorn recommendations_service:app
```

Сервис будет доступен по адресу: `http://127.0.0.1:8000`

### Описание эндпоинтов сервиса:

- `/recommendations` - Основной метод, который принимает запрос с идентификатором пользователя user_id и выдаёт рекомендации, учитывая историю пользователя и смешивая онлайн- и офлайн-рекомендации.
- `/get_online_rec` - Возвращает список онлайн-рекомендаций по k-последним событиям пользователя user_id, и по N-похожим трекам на каждое событие.
- `/put_user_event` - Сохраняет событие для user_id, item_id.
- `/get_user_events` - Возвращает список последних k событий для пользователя user_id.
- `/load_recommendations` - Загружает оффлайн-рекомендации из файла.
- `/get_statistics` - Выводит статистику по имеющимся счётчикам.

# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

Запустить тест можно командой:

```
python test_service.py
```

Лог тестирования сохраняется в `test_service.log` текущей папки

# Структура проекта

| Путь | Описание |
|------|----------|
| `recommendations_service.py` | Микросервис по рекомендациям |
| `test_service.py` | Тест микросервиса |
| `recsys/load_data.py` | Начальная загрузка данных |
| `utils/event_store.py` | Обработчик событий |
| `utils/recommendations.py` | Класс по работе с рекомендациями |
| `utils/utils.py` | Ютилиты микросервиса |
| `.env` | Параметры подключения |
| `README.md` | Информация о проекте |
| `recommendations.ipynb` | Расчет рекомендаций (первая часть проекта) |
| `requirements.txt` | Список зависимостей |

# Стратегия смешивания онлайн- и офлайн-рекомендаций

Стратегия смешивания онлайн- и офлайн-рекомендаций заключается в чередовании рекомендаций из обоих источников для обеспечения разнообразия и актуальности. Сначала берутся первые рекомендации из онлайн- и офлайн-списков, которые попеременно добавляются в общий список, затем оставшиеся рекомендации из более длинного списка дописываются в конец. После этого удаляются дубликаты с сохранением порядка, чтобы избежать повторений, и итоговый список обрезается до заданной длины k. Такой подход позволяет сочетать персонализированные долгосрочные предпочтения (офлайн) с актуальными действиями пользователя (онлайн).

# Выводы

Микросервис успешно обрабатывает запросы пользователей и формирует персонализированные рекомендации, комбинируя онлайн- и офлайн-стратегии. Вся история взаимодействий пользователя учитывается для повышения релевантности выдачи.

Код протестирован для всех возможных сценариев.