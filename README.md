# VeloRank (ВелоИндекс)

Система рейтингования велогонщиков на основе финишных протоколов соревнований. Использует алгоритм сравнения «каждый со всеми» (Pairwise Anchor Model).

## Архитектура
* **Backend:** Python 3, FastAPI, SQLAlchemy, SQLite.
* **Frontend:** React 18 (TypeScript), Vite, Tailwind CSS, Recharts.

---

## Запуск проекта

### Запуск Backend-сервиса (Python)

1. Перейдите в папку `backend/`:
   ```bash
   cd backend
   ```

2. Установите необходимые зависимости (рекомендуется использовать виртуальное окружение):
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите сервер (FastAPI с помощью Uvicorn):
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Сервер запустится на `http://localhost:8000`. Вы можете проверить API документацию на `http://localhost:8000/docs`.


### Запуск Frontend-приложения (React)

1. Перейдите в папку `frontend/`:
   ```bash
   cd frontend
   ```

2. Установите зависимости NPM:
   ```bash
   npm install
   ```

3. Запустите сервер для разработки:
   ```bash
   npm run dev
   ```
   Приложение откроется на `http://localhost:5173`. Убедитесь, что backend-сервер запущен и работает на `localhost:8000` для корректной загрузки данных.

---

## Загрузка данных и протоколов гонок

В системе предусмотрено два способа загрузки результатов (протоколов):

### 1. Автоматический парсинг (Scraping)
В проекте есть скрипт для автоматического сбора результатов с сайта `velomarathon.ru` и `timingband.ru`.
1. Убедитесь, что backend-сервер запущен.
2. Перейдите в папку `backend/`:
   ```bash
   cd backend
   ```
3. Запустите скрипт парсинга:
   ```bash
   python scripts/load_real_data.py
   ```
Скрипт автоматически найдет ссылки на протоколы, обработает их, сгенерирует уникальные ID для спортсменов (на основе их имени) и отправит результаты в базу данных.

### 2. Загрузка через API (Ручной ввод или интеграция)
Вы можете загружать любые другие финишные протоколы, отправляя POST-запрос на Endpoint `/api/v1/races`.

**Endpoint:** `POST http://localhost:8000/api/v1/races`

**Формат JSON-тела (Payload):**
```json
{
  "date": "2024-05-20",
  "category": "road",
  "k_factor": 1.2,
  "results": [
    {
      "rider_id": "r_ivan_petrov",
      "rider_name": "Иван Петров",
      "time_sec": 3600,
      "status": "FIN"
    },
    {
      "rider_id": "r_alex_smirnov",
      "rider_name": "Алексей Смирнов",
      "time_sec": 3840,
      "status": "FIN"
    }
  ]
}
```

* `category`: Дисциплина (`road`, `gravel`, `mtb`).
* `k_factor`: Коэффициент сложности гонки (по умолчанию 1.0).
* `time_sec`: Время прохождения дистанции в секундах.
* `status`: Статус финиша (`FIN`, `DNF`, `DSQ`). Участники со статусом отличным от `FIN` игнорируются при расчете рейтинга.
