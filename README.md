# ИИ-тренажёр для подготовки к устному экзамену по физике

Проверяет устный ответ обучающегося по заранее заданной рубрике с помощью LLM (Groq). Возвращает баллы по критериям, список пропусков, ошибки и оценку.

## Требования

- Python 3.10+
- API-ключ Groq
- Название модели Groq

Все команды выполняются из корня проекта.

## 1. Виртуальное окружение

python -m venv .venv

Активация окружения:

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows cmd
.venv\Scripts\activate.bat

## 2. Установка зависимостей

pip install -r requirements.txt

## 3. Настройка .env

Скопируйте пример конфигурации:

# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env

Заполните файл .env:

GROQ_API_KEY=ваш_ключ
GROQ_MODEL=название_модели

## 4. Запуск приложения

python -m streamlit run frontend/streamlit_app.py

## 5. Проверка данных

python scripts/validate_data.py

## 6. Тесты

pytest tests/ -q

## Пример .env

# GROQ_API_KEY=Ваш API
# GROQ_MODEL=Ваша модель
# TEMPERATURE=0.3
# MAX_TOKENS=1024
# VERIFIER_ENABLED=true
