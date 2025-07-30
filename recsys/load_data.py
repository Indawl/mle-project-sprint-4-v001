import boto3
from dotenv import load_dotenv
import os
from pathlib import Path

# Определяем базовые пути
SCRIPT_DIR = Path(__file__).parent.absolute()
BASE_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'recsys' else SCRIPT_DIR

# Загрузка переменных окружения
load_dotenv(BASE_DIR / '.env', override=True)

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

# Инициализация клиента S3
s3 = boto3.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Пути к файлам
files = {
    'recsys/data/items.parquet': SCRIPT_DIR / 'data/items.parquet',
    'recsys/models/als_model.npz': SCRIPT_DIR / 'models/als_model.npz',
    'recsys/recommendations/personal_als.parquet': SCRIPT_DIR / 'recommendations/personal_als.parquet',
    'recsys/recommendations/top_popular.parquet': SCRIPT_DIR / 'recommendations/top_popular.parquet'
}

# Создаем локальные директории, если они не существуют
for local_path in set(os.path.dirname(path) for path in files.values()):
    Path(local_path).mkdir(parents=True, exist_ok=True)

# Загрузка файлов
for s3_path, local_path in files.items():
    try:
        # Получаем объект из S3
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_path)
        
        # Сохраняем содержимое в локальный файл
        with open(local_path, 'wb') as f:
            f.write(response['Body'].read())

        print(f"Файл {s3_path} успешно загружен и сохранен как {local_path}")
    except Exception as e:
        print(f"Ошибка при загрузке {s3_path}: {str(e)}")
        