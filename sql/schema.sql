PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_interests (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interest TEXT NOT NULL,
    PRIMARY KEY (user_id, interest)
);

CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    address TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 0 AND 10),
    is_available INTEGER NOT NULL CHECK (is_available IN (0, 1))
);

CREATE TABLE IF NOT EXISTS place_availability (
    place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    is_available INTEGER NOT NULL CHECK (is_available IN (0, 1)),
    PRIMARY KEY (place_id, weekday)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    place_id INTEGER NOT NULL REFERENCES places(id),
    is_cancelled INTEGER NOT NULL CHECK (is_cancelled IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_places_category ON places(category_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_place ON recommendations(place_id);
