# Лабораторная работа №12: AI-ассистированная разработка

Студент: Мельникова Анастасия  
Группа: 220032-11  
Вариант: 13, повышенная сложность  
Предметная область: система управления логистикой

## Описание программы

Logistics Management System — REST API для управления логистикой: маршруты, транспортные средства, водители, заказы на доставку и GLONASS-телеметрия.

Реализовано:

- JWT-аутентификация: bootstrap администратора, логин, текущий пользователь.
- Роли доступа: `admin`, `dispatcher`, `viewer`.
- CRUD для водителей, транспортных средств, маршрутов и заказов.
- Назначение водителя и ТС на заказ с проверкой грузоподъемности.
- Прием GLONASS-координат и получение последней точки ТС.
- Аналитика: dashboard и отчет прибыльности маршрутов.
- Code review AI-кода и журнал промптов в `PROMPT_LOG.md`.
- GitHub Actions workflow для тестов и AI-summary Pull Request.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy 2
- Pydantic / pydantic-settings
- SQLite по умолчанию, конфигурация через `DATABASE_URL`
- pytest, pytest-cov, httpx
- Docker, docker-compose
- GitHub Actions

## Структура

```text
src/logistics_app/      исходный код приложения
tests/                  pytest-тесты
docs/                   материалы code review и SQL-аналитики
.github/workflows/      CI/CD workflow
```

## Сборка и запуск локально

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Создать демо-данные:

```bash
python -m logistics_app
```

Запустить API:

```bash
uvicorn logistics_app.main:app --reload
```

API будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Запуск через Docker

```bash
docker compose up --build
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
```

## Переменные окружения

```text
DATABASE_URL=sqlite:///./logistics.db
JWT_SECRET=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Примеры использования API

Создать первого администратора:

```bash
curl -X POST http://127.0.0.1:8000/auth/bootstrap-admin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@logistics.local\",\"full_name\":\"Admin User\",\"password\":\"Admin12345\",\"role\":\"admin\"}"
```

Получить JWT:

```bash
curl -X POST http://127.0.0.1:8000/auth/login ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin@logistics.local&password=Admin12345"
```

Создать маршрут:

```bash
curl -X POST http://127.0.0.1:8000/routes ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Moscow - Kazan\",\"origin\":\"Moscow\",\"destination\":\"Kazan\",\"distance_km\":820,\"planned_duration_min\":720}"
```

Создать транспортное средство:

```bash
curl -X POST http://127.0.0.1:8000/vehicles ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"plate_number\":\"А123ВС77\",\"model\":\"KAMAZ 5490\",\"capacity_kg\":20000}"
```

Создать заказ:

```bash
curl -X POST http://127.0.0.1:8000/orders ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"cargo_name\":\"Medical equipment\",\"weight_kg\":1200,\"customer_name\":\"Clinic Partner\",\"route_id\":1}"
```

Отправить GLONASS-точку:

```bash
curl -X POST http://127.0.0.1:8000/telemetry/glonass ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"vehicle_id\":1,\"latitude\":55.75,\"longitude\":37.61,\"speed_kmh\":67.5}"
```

Получить dashboard:

```bash
curl -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:8000/reports/dashboard
```

## Тесты и покрытие

```bash
pytest
```

Команда запускает unit/API-тесты и формирует `coverage.xml`.

## CI/CD и AI

Workflow `.github/workflows/ai-pr-summary.yml` запускается на Pull Request, выполняет тесты и публикует комментарий с описанием изменений. Если секрет `OPENAI_API_KEY` не задан, workflow оставляет детерминированный fallback-комментарий, чтобы проверка CI оставалась рабочей.

