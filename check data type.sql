-- 先看看order_date现在是什么格式
SELECT order_date, COUNT(*)
FROM mysql_ready
GROUP BY order_date
ORDER BY order_date
LIMIT 10;

-- 检查数据类型
DESCRIBE mysql_ready;

ALTER TABLE mysql_ready 
MODIFY COLUMN order_date DATE;