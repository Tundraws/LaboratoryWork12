# Лабораторная работа №12: AI-ассистированная разработка

Студент: Мельникова Анастасия  
Группа: 220032-11  
Номер лабораторной работы: 12  
Номер варианта: 13  
Тип варианта: повышенная сложность  
Предметная область: система управления логистикой

## Описание программы

Logistics Management System — FastAPI-приложение для управления логистикой. Система позволяет вести маршруты, транспортные средства, водителей, заказы на доставку и GLONASS-телеметрию.

Реализовано:

- JWT-аутентификация: создание первого администратора, логин, получение текущего пользователя.
- Роли доступа: `admin`, `dispatcher`, `viewer`.
- CRUD для маршрутов, транспортных средств, водителей и заказов.
- Связи между сущностями: заказ связан с маршрутом, водителем и ТС; GLONASS-точки связаны с ТС.
- Проверка грузоподъемности при назначении транспорта на заказ.
- Аналитика: dashboard и отчет по прибыльности маршрутов.
- Админ-функция просмотра пользователей.
- Docker-конфигурация и GitHub Actions workflow для Pull Request.
- Unit/API-тесты с покрытием около 93%.

## Язык программирования и технологии

- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Pydantic / pydantic-settings
- SQLite по умолчанию, настройка через `DATABASE_URL`
- pytest, pytest-cov, httpx
- Docker и docker-compose
- GitHub Actions

## Структура проекта

```text
src/logistics_app/      исходный код приложения
tests/                  pytest-тесты
docs/                   материалы code review и доказательство PR-комментария
.github/workflows/      CI/CD workflow
README.md               инструкция по сборке и запуску
PROMPT_LOG.md           журнал промптов по обязательным заданиям
```

## Инструкция по сборке

Создать виртуальное окружение и установить зависимости:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Проект использует `src/`-layout, поэтому для локального запуска из корня нужно добавить папку `src` в `PYTHONPATH`.

PowerShell:

```powershell
$env:PYTHONPATH = "src"
```

При необходимости можно создать демо-данные:

```bash
python -m logistics_app
```

## Инструкция по запуску

Запуск локально из PowerShell:

```powershell
$env:PYTHONPATH = "src"
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

Запуск через Docker:

```bash
docker compose up --build
```

Проверка работоспособности:

```bash
curl http://127.0.0.1:8000/health
```

## Переменные окружения

```text
DATABASE_URL=sqlite:///./logistics.db
JWT_SECRET=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

## Примеры API-запросов

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

Создать водителя:

```bash
curl -X POST http://127.0.0.1:8000/drivers ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"full_name\":\"Ivan Petrov\",\"license_number\":\"DRV202613\",\"phone\":\"+79001234567\"}"
```

Создать заказ:

```bash
curl -X POST http://127.0.0.1:8000/orders ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"cargo_name\":\"Medical equipment\",\"weight_kg\":1200,\"customer_name\":\"Clinic Partner\",\"route_id\":1}"
```

Назначить водителя и ТС на заказ:

```bash
curl -X POST http://127.0.0.1:8000/orders/1/assign ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"driver_id\":1,\"vehicle_id\":1}"
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
python -m pytest
```

Текущий результат: тесты проходят, покрытие около 93%.

## CI/CD и AI

Workflow `.github/workflows/ai-pr-review.yml` запускается на Pull Request, выполняет тесты и публикует комментарий с описанием изменений. Если секрет `OPENAI_API_KEY` не задан, workflow публикует fallback summary, чтобы CI оставался рабочим без внешнего API.
