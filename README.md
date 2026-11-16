# Сервис поиска мест по интересам

Учебный проект поиска мест для отдыха и досуга по интересам. Репозиторий сохраняет исходное Flask-приложение и консольную объектную модель, а практические работы №5–7 последовательно добавляют Django-интерфейс, шаблоны и отдельный слой SQLite на стандартном `sqlite3`. С ПР9 предметные данные хранятся в моделях Django и читаются через ORM.

## Запуск Django-версии

Требуется Python 3.10+ и зависимости из `requirements.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data/fixtures/demo.json
python manage.py runserver
```

Вместо демонстрационного fixture можно перенести исходные данные ПР7: `python -m db.import_json` (создаёт `data/places.sqlite3`), затем `python db/import_sqlite_to_orm.py`.

Для Linux/macOS активируйте окружение командой `source .venv/bin/activate`. Django-сервер откроется по адресу `http://127.0.0.1:8000`.

Основные страницы:

- `/` — главная страница и категории;
- `/places/` — каталог: поиск по названию и адресу, фильтр по категории и рейтингу, сортировка;
- `/places/1/` — карточка места с графиком работы и активными рекомендациями;
- `/recommendations/` — список рекомендаций с фильтрами по дате, месту, пользователю и статусу, сортировкой и пагинацией;
- `/recommendations/1/` — карточка рекомендации;
- `/places/available/?date=2026-10-26` — доступные места;
- `/places/statistics/` — статистика по категориям.

Дата на странице доступности влияет на результат: место показывается, если в его графике (`PlaceAvailability`) этот день недели отмечен как открытый и у места установлен общий флаг `is_available`.

## Практическая работа №5 — Django, HTTP и основы веб-разработки

Django-проект `roomly` размещён в корне репозитория. Приложения `homepage`, `places` и `recommendations` зарегистрированы в настройках. В приложениях есть именованные маршруты с пространством имён, страницы главной, каталога, карточки места и рекомендаций, а также обработка отсутствующего объекта через HTTP 404. На этапе ПР5 `inline_views.py` показывает формирование HTML-ответов и чтение исходных JSON-данных. Исходный Flask-сервис и консольная версия сохранены.

## Практическая работа №6 — шаблоны Django

Страницы переведены на `render()` и шаблоны в `templates/`: общий `base.html`, наследование через блоки, включаемые карточки и строка рекомендации, контекст, циклы, условия и обработка пустых списков. Именованные URL используются в навигации, стили и JavaScript находятся в `static/django/`, для иллюстрации карточек добавлен SVG. Представления ПР6 продолжают читать прежние JSON-файлы; `views.py` сохраняет этот этап перехода.

## Практическая работа №7 — SQL и SQLite

Доменная база данных создаётся по `sql/schema.sql`. Таблицы `categories`, `users`, `user_interests`, `places` и `recommendations` имеют первичные и внешние ключи. Команда `python -m db.import_json` переносит исходные данные из JSON и может безопасно запускаться повторно. Подключение находится в `db/database.py`: включены `PRAGMA foreign_keys = ON` и `sqlite3.Row`.

В `sql/queries.sql` приведены 13 запросов с `SELECT`, `WHERE`, `JOIN`, параметрами, агрегатами, `GROUP BY`, `HAVING`, `LIMIT` и `OFFSET`. Django-представления из `sql_views.py` используют SQLite для главной страницы, каталога, поиска, карточки, рекомендаций, статистики и графика доступности по выбранной дате. Значения фильтра передаются параметрами `?`.

После импорта JSON SQLite-файл находится в `data/places.sqlite3`. Состояние ПР7 доступно через `roomly/pr7_urls.py` (`sql_views.py`, `sql_urls.py`) и проверяется тестами `tests/test_pr7_sql.py`.

## Практическая работа №9 — Django ORM, модели и миграции

Слой данных переведён с `sqlite3` на Django ORM. Целевая база — `data/django.sqlite3` (настройка `DATABASES`), исходная база ПР7 `data/places.sqlite3` не изменяется и используется только как источник переноса.

Модели и связи:

| Модель | Приложение | Поля | Связи |
| --- | --- | --- | --- |
| `Category` | `places` | `name` (уникальное), `description` | — |
| `Place` | `places` | `name`, `address`, `rating` (0–10), `is_available` | `category` → `Category` (`PROTECT`, `related_name="places"`) |
| `PlaceAvailability` | `places` | `weekday` (0 — понедельник), `is_available` | `place` → `Place` (`CASCADE`, `related_name="schedule"`), уникальная пара место + день |
| `User` | `users` | `name`, `email` | `interests` ↔ `Category` (многие ко многим) |
| `Recommendation` | `recommendations` | `visit_date`, статус, `created_at` | `user` → `User`, `place` → `Place` (`PROTECT`, `related_name="recommendations"`) |

`PROTECT` не даёт удалить место, категорию или пользователя, на которых ссылаются рекомендации, — история сохраняется.

Порядок работы с базой:

```powershell
python manage.py makemigrations   # сформировать миграции по моделям
python manage.py migrate          # применить миграции
python manage.py showmigrations   # проверить состояние
python db/inspect_source_db.py    # (только чтение) структура и проверки базы ПР7
python db/import_sqlite_to_orm.py # перенос данных ПР7 с сохранением id и связей
```

Скрипт переноса сохраняет первичные ключи, переводит интересы из `user_interests` в связь многие-ко-многим, пересчитывает день недели из формата SQLite (`0` — воскресенье) в формат Python (`0` — понедельник). У рекомендаций ПР7 не было даты, поэтому им назначается демонстрационная дата `2026-10-29`. Повторный запуск обновляет записи, не создавая дублей. Fixture `data/fixtures/demo.json` получен командой `dumpdata` и содержит расширенный демонстрационный набор (6 мест, 3 пользователя, 12 рекомендаций).

Представления `views.py` всех приложений получают данные только через ORM: `all()`, `get_object_or_404()`, `filter()`/`exclude()`, поиск `icontains` по нескольким полям через `Q`, фильтры по связанным моделям (`schedule__weekday`, `place__category`), сортировка по словарю разрешённых полей, `select_related()`/`prefetch_related()`, `annotate()` с `F()`/`Count()`/`Avg()`/`Subquery`, `aggregate()`, срез `[:3]` и `Paginator` с навигацией через `{% querystring %}`. Состояние ПР6 сохранено в `json_views.py`/`json_urls.py` (`roomly/pr6_urls.py`).

## Проверка

```powershell
python manage.py check
python manage.py showmigrations
pytest -v
flake8 . --extend-exclude=venv
```

## Сохранённое Flask-приложение

Исходный Flask REST API и интерфейс доступны отдельно:

```powershell
python app.py
```

API и контейнерная конфигурация Flask сохранены для предыдущей версии проекта; Docker Compose запускает именно Flask-приложение.

## Структура

```text
roomly/                   настройки и корневые URL Django (+ pr5/pr6/pr7_urls чекпоинты)
homepage/                 главная страница
places/                   модели Category, Place, PlaceAvailability; каталог, доступность, статистика
users/                    модель пользователя предметной области
recommendations/          модель Recommendation; список и карточка рекомендаций
models/                   исходная предметная модель
storage.py                 исходное JSON-хранилище
db/                       sqlite3-слой ПР7, инспекция и перенос данных в ORM
sql/                       схема и учебные SQL-запросы
templates/                шаблоны Django
static/django/            CSS, JavaScript и SVG
data/                     исходные JSON, fixtures/demo.json, локальные базы SQLite
```
