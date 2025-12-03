# Описание проекта
Микросервисное приложение для классификации мобильных телефонов по ценовому диапазону на основе их характеристик. Проект включает полный stack для разработки, тестирования, мониторинга и хранения данных.


### Целевая переменная
**price_range** — ценовой диапазон телефона (0-3):
- **0**: бюджетные телефоны
- **1**: телефоны низко-среднего сегмента
- **2**: телефоны среднего и высокого сегмента
- **3**: премиум телефоны

### Используемые технологии и библиотеки

#### Backend & ML:
- **FastAPI** — асинхронный веб-фреймворк для создания API
- **scikit-learn** — машинное обучение и предсказания
- **pandas** — обработка и анализ данных
- **numpy** — работа с массивами
- **pickle** — сериализация моделей

#### Контейнеризация:
- **Docker** — контейнеризация сервисов
- **Docker Compose** — оркестрация микросервисов

#### Базы данных:
- **PostgreSQL 15** — хранение входных данных и предсказаний
- **pgAdmin 4** — веб-интерфейс управления БД

#### Мониторинг и визуализация:
- **Prometheus** — сбор и хранение метрик
- **Grafana** — визуализация метрик на дашборде
- **prometheus-fastapi-instrumentator** — автоматический сбор метрик из FastAPI


## Результаты разведочного анализа (EDA)

### Действия по очистке данных:
1. Удалены записи с нулевыми значениями в полях:
   - sc_w (ширина экрана)
   - pc (основная камера)
   - fc (фронтальная камера)
   - px_height (высота в пикселях)
2. Оптимизированы типы данных для всех столбцов
3. Проверено отсутствие дубликатов
4. Проверено отсутствие пропущенных значений

### Основные выводы:
1. [Распределение мощности батареи](./eda/battery_distribution.png):
   - Наблюдается равномерное распределение
   - Отсутствуют явные выбросы

2. [RAM vs Ценовой диапазон](./eda/ram_price_scatter.png):
   - Выявлена сильная положительная корреляция
   - Чем больше RAM, тем выше ценовой диапазон
   - Четкое разделение ценовых категорий

3. [Разрешение экрана](./eda/resolution.png):
   - Линейная зависимость между высотой и шириной
   - Стандартное соотношение сторон у большинства устройств

4. [Матрица корреляций](./eda/correlation_matrix.png):
   - Наибольшая корреляция с ценой у RAM (0.92)
   - Умеренная корреляция у battery_power (0.22)
   - Слабые корреляции между остальными признаками

5. [Интерактивный график RAM vs Батарея](./eda/interactive_plot.html):
   - Подтверждает важность RAM для определения цены
   - Показывает кластеризацию устройств по ценовым категориям


## Запуск проекта
```bash
git clone https://github.com/DashinIN/ISS_Labs.git
cd IIS-Labs
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

## Структура проекта
- `data/` - исходные и очищенные данные
- `eda/` - графики и результаты анализа
- `requirements.txt` - зависимости проекта

# Запуск MLFlow
1. Перейти в директорию ./mlflow:
```
   cd mlflow/
```
2. Выполнить скрипт для запуска сервера:
```
   sh run.sh
```
## Структура проекта

```
my_proj/
├── .venv_my_proj/              # Виртуальное окружение Python
├── .git/                        # Git репозиторий
├── data/                        # Исходные и очищенные данные
├── eda/                         # Графики и результаты анализа
├── research/                    # Ноутбуки и исследования
├── services/                    # Микросервисы
│   ├── ml_service/             # Основной ML-сервис
│   │   ├── api_handler.py      # Обработчик предсказаний
│   │   ├── db_handler.py       # Работа с БД
│   │   ├── main.py             # Главное приложение FastAPI
│   │   ├── Dockerfile          # Docker образ
│   │   └── requirements.txt     # Python зависимости
│   │   
│   ├── requests/               # Тестовый клиент
│   │   ├── req.py              # Генератор тестовых запросов
│   │   ├── Dockerfile          # Docker образ
│   │   └── requirements.txt     # Python зависимости
│   ├── prometheus/             # Prometheus мониторинг
│   │   └── prometheus.yml      # Конфигурация Prometheus
│   ├── grafana/                # Grafana дашборды
│   │   └── config.json         # Конфиг дашборда
│   ├── database/               # PostgreSQL данные
│   │   ├── data/               # Volume для данных PostgreSQL
│   │   └── pgadmin/            # Volume для pgAdmin
│   ├── models/                 # Сохраненные модели
│   │   └── get_model.py        # Загрузка модели
│   └── compose.yml             # Docker Compose конфигурация
├── .gitignore 
```

---

## Микросервисы

### 1. ML Service (`ml_service/`)

**Основной API-сервис на FastAPI для предсказания ценовых диапазонов телефонов.**

**Структура файлов:**
- `main.py` — главное приложение с маршрутами:
  - `GET /` — информация о сервисе
  - `POST /api/prediction` — запрос на предсказание
  - `GET /metrics` — метрики Prometheus
  
- `api_handler.py` — обработчик предсказаний:
  - Загрузка модели из `model.pkl`
  - Преобразование входных данных в DataFrame
  - Возврат предсказания (0-3)
  
- `db_handler.py` — работа с PostgreSQL:
  - Сохранение входных данных в таблицу `phone_requests`
  - Сохранение предсказаний в таблицу `phone_predictions`
  
- `requirements.txt` — зависимости:
  ```
   fastapi
   uvicorn
   pandas
   pickle4
   scikit-learn
   prometheus_fastapi_instrumentator
   psycopg2-binary
   python-multipart
  ```

---

### 2. Test Requests (`requests/`)

**Тестовый клиент для генерации нагрузки на API.**

**Структура файлов:**
- `req.py` — генератор 50 случайных запросов:
  - Создает синтетические данные о телефонах
  - Отправляет POST запросы на `/api/prediction`
  - Логирует результаты
  
- `requirements.txt` — зависимости:
  ```
  requests
  ```

---

### 3. PostgreSQL Database (`database/`)

**Реляционная БД для хранения данных и предсказаний.**

**Структура БД:**

[Таблицы](./services/database/db.png)

```sql
-- Таблица входных данных
CREATE TABLE phone_requests (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    battery_power INT,
    blue INT,
    clock_speed FLOAT,
    dual_sim INT,
    fc INT,
    four_g INT,
    int_memory INT,
    m_dep FLOAT,
    mobile_wt INT,
    n_cores INT,
    pc INT,
    px_height INT,
    px_width INT,
    ram INT,
    sc_h INT,
    sc_w INT,
    talk_time INT,
    three_g INT,
    touch_screen INT,
    wifi INT
);

-- Таблица предсказаний
CREATE TABLE phone_predictions (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_id INT REFERENCES phone_requests(id),
    predicted_price INT
);
```

**Структура файлов:**
- `data/` — volume для хранения данных PostgreSQL
- `pgadmin/` — volume для хранения конфигурации pgAdmin

---

### 4. pgAdmin (`database/pgadmin/`)

**Веб-интерфейс управления PostgreSQL.**

**Доступ:** http://localhost:5050


**Возможности:**
- Просмотр таблиц `phone_requests` и `phone_predictions`
- Выполнение SQL запросов
- Анализ данных

---

### 5. Prometheus (`prometheus/`)

**Система мониторинга для сбора метрик сервисов.**

**Структура файлов:**
- `prometheus.yml` — конфигурация:

**Доступ:** http://localhost:9090

### 6. Grafana (`grafana/`)

**Визуализация метрик на интерактивном дашборде.**

[Дашборд](./services/graphana/dashboard.png)

json дашборда хранится в директории `grafana/`.

**Доступ:** http://localhost:3000

**Дашборд включает панели:**

#### Панель: Request Rate (Infrastructure)
- **Метрика:** `rate(prediction_requests_total[1m])`
- **Описание:** Частота HTTP запросов в секунду
- **Единица:** req/s

#### Панель: Response Time Percentiles (Infrastructure)
- **Метрика:** `histogram_quantile(0.95, prediction_response_time)`
- **Описание:** Время ответа (p95, p99)
- **Единица:** ms

#### Панель: Prediction Success vs Errors (Application)
- **Метрика:** 
  - Успешные: `prediction_requests_total{status="success"}`
  - Ошибки: `prediction_errors_total`
- **Описание:** Соотношение успешных ответов к ошибкам
- **Тип:** Pie Chart

#### Панель: Model Prediction Distribution (Model Quality)
- **Метрика:** `model_prediction_distribution_bucket`
- **Описание:** Распределение предсказанных ценовых диапазонов (0-3)
- **Тип:** Histogram

#### Панель: Predictions Count from Database (PostgreSQL)
- **Запрос:** 
  ```sql
  SELECT COUNT(*) as total_predictions FROM phone_predictions;
  SELECT COUNT(*) as total_requests FROM phone_requests;
  ```
- **Описание:** Количество записей в БД
- **Тип:** Gauge

---

## Запуск проекта

### Предварительные требования:
- Docker & Docker Compose
- Python 3.8+
- Git

### Быстрый старт

#### 1. Клонирование репозитория:
```bash
git clone https://github.com/DashinIN/ISS_Labs.git
cd IIS-Labs
```

#### 2. Создание виртуального окружения:
```bash
python -m venv .venv
.venv\Scripts\activate  # На Windows
# или
source .venv/bin/activate  # На Linux/Mac
```

#### 3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

#### 4. Запуск Docker Compose: 
Собрать сервисы, после: 
```bash
cd services
docker compose up -d
```

## Веб-интерфейсы

| Сервис | URL | Учетные данные |
|--------|-----|----------------|
| **API Документация** | http://localhost:8000/docs | — |
| **Swagger UI** | http://localhost:8000/redoc | — |
| **Prometheus** | http://localhost:9090 | — |
| **Grafana** | http://localhost:3000 | admin/admin |
| **pgAdmin** | http://localhost:5050 | admin@admin.com/admin |

---

## Использование API

### Пример запроса на предсказание:

[Пример запроса](./services/requests/images/req.png)

```bash
curl -X POST "http://localhost:8000/api/prediction?phone_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "battery_power": 1500,
    "blue": 1,
    "clock_speed": 2.5,
    "dual_sim": 1,
    "fc": 15,
    "four_g": 1,
    "int_memory": 32,
    "m_dep": 0.8,
    "mobile_wt": 150,
    "n_cores": 4,
    "pc": 12,
    "px_height": 1080,
    "px_width": 720,
    "ram": 3000,
    "sc_h": 16,
    "sc_w": 9,
    "talk_time": 10,
    "three_g": 1,
    "touch_screen": 1,
    "wifi": 1
  }'
```

### Ответ:
```json
{
  "price": 2,
  "phone_id": 1
}
```

---

## Запуск MLFlow (опционально)

```bash
cd mlflow/
sh run.sh
```

Сервер MLFlow будет доступен на http://localhost:5000

---


## Структура запросов в тестовом клиенте

Тестовый скрипт генерирует 50 запросов со следующей структурой:

```python
data = {
    "battery_power": randint(500, 1999),      # Емкость батареи мАч
    "blue": randint(0, 1),                    # Наличие Bluetooth
    "clock_speed": uniform(0.5, 3.0),         # Частота процессора ГГц
    "dual_sim": randint(0, 1),                # Наличие двух SIM карт
    "fc": randint(0, 19),                     # Фронтальная камера МПикс
    "four_g": randint(0, 1),                  # Наличие 4G
    "int_memory": randint(2, 64),             # Встроенная память ГБ
    "m_dep": uniform(0.1, 1.0),               # Толщина мм
    "mobile_wt": randint(80, 200),            # Вес граммов
    "n_cores": randint(1, 8),                 # Количество ядер
    "pc": randint(0, 20),                     # Основная камера МПикс
    "px_height": randint(0, 1907),            # Разрешение высота пиксели
    "px_width": randint(501, 1988),           # Разрешение ширина пиксели
    "ram": randint(263, 3989),                # ОЗУ МБ
    "sc_h": randint(5, 19),                   # Размер экрана высота см
    "sc_w": randint(0, 18),                   # Размер экрана ширина см
    "talk_time": randint(2, 20),              # Время разговора часы
    "three_g": randint(0, 1),                 # Наличие 3G
    "touch_screen": randint(0, 1),            # Сенсорный экран
    "wifi": randint(0, 1)                     # Наличие WiFi
}
```

---

## Лицензия

MIT License

---

## Контакты

Проект создан в рамках лабораторных работ по ИИС.