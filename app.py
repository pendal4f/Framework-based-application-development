from __future__ import annotations

import hmac
import os
import secrets
import shutil
import threading
import time
from copy import deepcopy
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import check_password_hash

from services import cancel_recommendation, create_recommendation
from storage import (
    CATEGORIES_FILE,
    DATA_DIR,
    PLACES_FILE,
    RECOMMENDATIONS_FILE,
    USERS_FILE,
    load_categories,
    load_places,
    load_recommendations,
    load_users,
    save_recommendations,
)

app = Flask(__name__)
secret_key = os.environ.get("APP_SECRET_KEY")
if not secret_key and os.environ.get("APP_ENV") == "production":
    raise RuntimeError("APP_SECRET_KEY must be set in production")
app.config.update(
    SECRET_KEY=secret_key or "local-development-key-change-before-deploying",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    MAX_CONTENT_LENGTH=16 * 1024,
)

_lock = threading.RLock()
_cache: dict[str, tuple[float, list[dict]]] = {}
_cache_ttl = max(1, int(os.environ.get("API_CACHE_TTL_SECONDS", "30")))


def _initialize_data_volume() -> None:
    source_dir = Path(__file__).resolve().parent / "data"
    if DATA_DIR.resolve() == source_dir.resolve():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ("users.json", "categories.json", "places.json", "recommendations.json"):
        target = DATA_DIR / filename
        source = source_dir / filename
        if not target.exists() and source.exists():
            shutil.copyfile(source, target)


_initialize_data_volume()


def _cached(key: str, loader) -> list[dict]:
    now = time.monotonic()
    item = _cache.get(key)
    if item and item[0] > now:
        return deepcopy(item[1])
    result = loader()
    _cache[key] = (now + _cache_ttl, deepcopy(result))
    return result


def _invalidate_cache() -> None:
    _cache.clear()


def _load_catalog() -> tuple[list, list, list, list]:
    users = load_users(USERS_FILE)
    categories = load_categories(CATEGORIES_FILE)
    places = load_places(categories, PLACES_FILE)
    recommendations = load_recommendations(users, places, RECOMMENDATIONS_FILE)
    return users, categories, places, recommendations


def _error(message: str, status: int):
    return jsonify(error=message), status


def _require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return _error("Требуется авторизация", 401)
        return view(*args, **kwargs)

    return wrapped


def _require_csrf() -> bool:
    supplied = request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_token", "")
    return bool(expected) and hmac.compare_digest(supplied, expected)


@app.after_request
def set_security_and_cache_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    )
    if request.path.startswith("/api/"):
        if request.path in {"/api/places", "/api/categories"} and request.method == "GET":
            response.headers.setdefault("Cache-Control", f"public, max-age={_cache_ttl}")
        else:
            response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/categories")
def categories_endpoint():
    categories = _cached(
        "categories",
        lambda: [item.to_data() for item in load_categories(CATEGORIES_FILE)],
    )
    return jsonify(categories)


@app.get("/api/places")
def places_endpoint():
    def load_data():
        categories = load_categories(CATEGORIES_FILE)
        return [place.to_data() | {"category_name": place.category.name}
                for place in load_places(categories, PLACES_FILE)]

    places = _cached("places", load_data)
    query = request.args.get("q", "").strip().casefold()
    category_id = request.args.get("category_id", type=int)
    min_rating = request.args.get("min_rating", default=0, type=int)
    if not 0 <= min_rating <= 10:
        return _error("Минимальный рейтинг должен быть от 0 до 10", 400)
    if query:
        places = [place for place in places if query in place["name"].casefold()]
    if category_id is not None:
        places = [place for place in places if place["category_id"] == category_id]
    places = [place for place in places if place["rating"] >= min_rating and place["is_available"]]
    return jsonify(places)


@app.get("/api/auth/csrf")
def csrf_token():
    token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return jsonify(csrf_token=token, authenticated=bool(session.get("authenticated")))


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = os.environ.get("ADMIN_USERNAME", "")
    password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    password = os.environ.get("ADMIN_PASSWORD", "")
    if not username or not (password_hash or password):
        return _error("Учётные данные администратора не настроены", 503)
    supplied_name = str(payload.get("username", ""))
    supplied_password = str(payload.get("password", ""))
    valid_password = (
        check_password_hash(password_hash, supplied_password)
        if password_hash else hmac.compare_digest(supplied_password, password)
    )
    if not hmac.compare_digest(supplied_name, username) or not valid_password:
        return _error("Неверное имя пользователя или пароль", 401)
    session.clear()
    session["authenticated"] = True
    session["csrf_token"] = secrets.token_urlsafe(32)
    return jsonify(authenticated=True, csrf_token=session["csrf_token"])


@app.post("/api/auth/logout")
@_require_auth
def logout():
    if not _require_csrf():
        return _error("Недействительный CSRF-токен", 403)
    session.clear()
    return jsonify(authenticated=False)


@app.get("/api/users")
@_require_auth
def users_endpoint():
    users = [user.to_data() for user in load_users(USERS_FILE)]
    return jsonify(users)


@app.get("/api/recommendations")
@_require_auth
def recommendations_endpoint():
    users, _, places, recommendations = _load_catalog()
    user_names = {user.id: user.name for user in users}
    place_names = {place.id: place.name for place in places}
    return jsonify([
        item.to_data() | {
            "user_name": user_names[item.user.id],
            "place_name": place_names[item.place.id],
            "status": item.status,
        }
        for item in recommendations
    ])


@app.post("/api/recommendations")
@_require_auth
def create_recommendation_endpoint():
    if not _require_csrf():
        return _error("Недействительный CSRF-токен", 403)
    payload = request.get_json(silent=True) or {}
    try:
        user_id = int(payload["user_id"])
        place_id = int(payload["place_id"])
        with _lock:
            users, _, places, recommendations = _load_catalog()
            recommendation = create_recommendation(
                recommendations, users, places, user_id, place_id
            )
            save_recommendations(recommendations, RECOMMENDATIONS_FILE)
        _invalidate_cache()
    except (KeyError, TypeError, ValueError) as error:
        return _error(str(error) or "Нужны user_id и place_id", 400)
    return jsonify(recommendation.to_data()), 201


@app.post("/api/recommendations/<int:recommendation_id>/cancel")
@_require_auth
def cancel_recommendation_endpoint(recommendation_id: int):
    if not _require_csrf():
        return _error("Недействительный CSRF-токен", 403)
    try:
        with _lock:
            users, _, places, recommendations = _load_catalog()
            cancel_recommendation(recommendations, recommendation_id)
            save_recommendations(recommendations, RECOMMENDATIONS_FILE)
        _invalidate_cache()
    except ValueError as error:
        return _error(str(error), 404)
    return jsonify(status="отменена")


@app.errorhandler(413)
def request_too_large(_error):
    return _error("Размер запроса превышает допустимый", 413)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
