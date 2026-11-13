# ИИ-тренажёр для подготовки к устному экзамену по физике

Проверяет устный ответ студента по заранее заданной рубрике с помощью LLM (Groq).
Возвращает баллы по критериям, список пропусков, ошибки и оценку.

## Запуск

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Измените `.env.example` вставив туда свой API и название модели.
4. `streamlit run frontend/streamlit_app.py`

## Проверка данных

`python scripts/validate_data.py`

## Тесты

`pytest tests/ -q`

## Запуск - 'python -m streamlit run frontend/streamlit_app.py' в терминал.