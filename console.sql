-- SELECT
--     pr.id, pr.date "Record date", p.name "Product name",
--     pr.quantity "Total work", COUNT(pr.id) "Total employees"
-- FROM attendance a
-- JOIN employees e ON e.id = a.employee_id
-- JOIN production_records pr ON pr.id = a.production_record_id
-- JOIN products p ON p.id = pr.product_id
-- GROUP BY pr.id, pr.date, p.name
-- ORDER BY pr.date;

SELECT
    a.employee_id, p.name, ROUND(pr.quantity::numeric/COUNT(a.id) * 700, 2)
FROM attendance a
JOIN production_records pr ON pr.id = a.production_record_id
JOIN products p ON p.id = pr.product_id
GROUP BY a.employee_id, p.name, pr.quantity;


SELECT e.first_name, ROUND(sum(records.salary), -3) as salary
FROM (
    SELECT
        a.employee_id, p.name, ROUND(pr.quantity::numeric/COUNT(a.id) * 700, 2) salary
    FROM attendance a
    JOIN production_records pr ON pr.id = a.production_record_id
    JOIN products p ON p.id = pr.product_id
    GROUP BY a.employee_id, p.name, pr.quantity
    ) records
JOIN employees e ON e.id=records.employee_id
GROUP BY e.first_name
ORDER BY e.first_name;

SELECT
    e.first_name,
    ROUND(SUM(ROUND((pr.quantity::numeric / COUNT(a.employee_id) OVER (PARTITION BY pr.id)) * 700, 2)), 2) AS salary
FROM attendance a
JOIN production_records pr ON pr.id = a.production_record_id
JOIN employees e ON e.id = a.employee_id
GROUP BY e.first_name
ORDER BY e.first_name;

