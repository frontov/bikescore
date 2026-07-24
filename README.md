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
