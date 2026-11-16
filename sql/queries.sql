-- 1. Полный список мест
SELECT id, name, address, rating FROM places ORDER BY name;

-- 2. Список мест по рейтингу (LIMIT/OFFSET)
SELECT id, name, rating FROM places ORDER BY rating DESC LIMIT ? OFFSET ?;

-- 3. Поиск места по идентификатору (WHERE)
SELECT * FROM places WHERE id = ?;

-- 4. Поиск мест по подстроке названия и диапазону рейтинга (WHERE)
SELECT * FROM places WHERE name LIKE ? AND rating >= ? ORDER BY rating DESC;

-- 5. Фильтрация по категории и доступности
SELECT * FROM places WHERE category_id = ? AND is_available = 1;

-- 6. Связанные данные места и категории (JOIN)
SELECT places.name, categories.name AS category, places.rating
FROM places JOIN categories ON categories.id = places.category_id;

-- 7. Рекомендации с именами пользователя и места (JOIN)
SELECT users.name, places.name AS place, recommendations.is_cancelled
FROM recommendations
JOIN users ON users.id = recommendations.user_id
JOIN places ON places.id = recommendations.place_id;

-- 8. Число мест и средний рейтинг (агрегаты)
SELECT COUNT(*) AS places_count, ROUND(AVG(rating), 1) AS average_rating
FROM places;

-- 9. Число активных рекомендаций (агрегат и WHERE)
SELECT COUNT(*) AS active_recommendations
FROM recommendations WHERE is_cancelled = 0;

-- 10. Количество и средний рейтинг мест по категории (GROUP BY)
SELECT categories.name, COUNT(places.id) AS places_count,
       ROUND(AVG(places.rating), 1) AS average_rating
FROM categories LEFT JOIN places ON places.category_id = categories.id
GROUP BY categories.id, categories.name;

-- 11. Категории с хотя бы одним местом (HAVING)
SELECT categories.name, COUNT(places.id) AS places_count
FROM categories LEFT JOIN places ON places.category_id = categories.id
GROUP BY categories.id, categories.name HAVING COUNT(places.id) > 0;

-- 12. Количество активных рекомендаций по категории (JOIN/GROUP BY)
SELECT categories.name, COUNT(recommendations.id) AS recommendation_count
FROM categories
LEFT JOIN places ON places.category_id = categories.id
LEFT JOIN recommendations ON recommendations.place_id = places.id
  AND recommendations.is_cancelled = 0
GROUP BY categories.id, categories.name;

-- 13. Поиск доступных мест на выбранную дату (день недели вычисляется SQLite)
SELECT places.name, places.address, places.rating
FROM places JOIN place_availability
  ON place_availability.place_id = places.id
WHERE places.is_available = 1
  AND place_availability.weekday = CAST(strftime('%w', ?) AS INTEGER)
  AND place_availability.is_available = 1
ORDER BY places.rating DESC;
