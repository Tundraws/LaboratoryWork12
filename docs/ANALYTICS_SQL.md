# Аналитический SQL-запрос

Задача: показать прибыльность маршрутов логистической системы: количество заказов, общий вес груза и расчетную выручку. Для учебного расчета используется ставка `0.035` за килограмм на километр.

```sql
SELECT
    r.id AS route_id,
    r.name AS route_name,
    COUNT(o.id) AS orders_count,
    COALESCE(SUM(o.weight_kg), 0) AS total_weight_kg,
    ROUND(COALESCE(SUM(o.weight_kg * r.distance_km * 0.035), 0), 2) AS estimated_revenue
FROM routes r
LEFT JOIN delivery_orders o ON o.route_id = r.id
GROUP BY r.id, r.name
ORDER BY orders_count DESC, r.name ASC;
```

Логика: маршруты берутся как основная таблица, чтобы в отчете были даже маршруты без заказов. `LEFT JOIN` подключает заказы, `GROUP BY` группирует строки по маршрутам, а `COALESCE` защищает отчет от `NULL` при отсутствии заказов.

