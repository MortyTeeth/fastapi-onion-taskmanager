# Async Task Manager — FastAPI + Onion Architecture

Полностью рабочий асинхронный таск-менеджер с чистой архитектурой.

## Особенности
- Полный CRUD задач с отношениями (автор, исполнитель, доска, наблюдатели)
- Фильтрация по `author_id`, `status`, `assignee_id`
- Async SQLAlchemy 2.0 + UoW + Repository pattern
- Чистый Swagger без дублей
- Alembic миграции