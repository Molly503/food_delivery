SELECT * FROM food_delivery.delivery_data;

-- 1. 每日运营核心KPI表
-- ================================
CREATE VIEW daily_operations_kpi AS
SELECT 
    order_date,
    COUNT(*) as total_orders,
    COUNT(DISTINCT rider_id) as active_riders,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rider_rating,
    
    -- 效率指标
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT rider_id), 2) as orders_per_rider,
    SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) as on_time_orders,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    
    -- 质量指标
    SUM(CASE WHEN rider_rating >= 4.5 THEN 1 ELSE 0 END) as high_rating_orders,
    ROUND(SUM(CASE WHEN rider_rating >= 4.5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as high_rating_rate,
    
    -- 异常指标
    SUM(CASE WHEN delivery_time > 60 THEN 1 ELSE 0 END) as delayed_orders,
    ROUND(SUM(CASE WHEN delivery_time > 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as delay_rate,
    
    -- 节日标识
    MAX(is_festival) as is_festival_day
FROM mysql_ready
GROUP BY order_date
ORDER BY order_date;

-- 2. 城市运营表现分析表
-- ================================
CREATE VIEW city_performance_analysis AS
SELECT 
    city_type,
    order_date,
    COUNT(*) as orders,
    COUNT(DISTINCT rider_id) as riders,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rating,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT rider_id), 2) as orders_per_rider,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    
    -- 订单类型分布
    ROUND(SUM(CASE WHEN order_type = 'Meal' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as meal_rate,
    ROUND(SUM(CASE WHEN order_type = 'Snack' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as snack_rate,
    ROUND(SUM(CASE WHEN order_type = 'Drinks' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as drinks_rate,
    
    -- 多重配送分析
    ROUND(SUM(CASE WHEN multi_delivery >= 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as multi_delivery_rate
FROM mysql_ready
GROUP BY city_type, order_date
ORDER BY order_date, city_type;

-- 3. 时段运营分析表
-- ================================
CREATE VIEW hourly_operations_analysis AS
SELECT 
    order_hour,
    CASE 
         WHEN order_hour BETWEEN 6 AND 10 THEN 'Breakfast'
        WHEN order_hour BETWEEN 11 AND 14 THEN 'Lunch'
        WHEN order_hour BETWEEN 17 AND 21 THEN 'Dinner'
        ELSE 'Off_Peak'
    END as time_period,
    order_date,
    COUNT(*) as orders,
    COUNT(DISTINCT rider_id) as active_riders,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rating,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    
    -- 计算相对于日均值的表现
    ROUND(AVG(delivery_time) - (
        SELECT AVG(delivery_time) 
        FROM mysql_ready mr2 
        WHERE DATE(mr2.order_date) = DATE(mysql_ready.order_date)
    ), 2) as delivery_time_vs_daily_avg
FROM mysql_ready
WHERE order_hour IS NOT NULL
GROUP BY order_hour, time_period, order_date
ORDER BY order_date, order_hour;

-- 4. 骑手绩效分析表
-- ================================
DROP VIEW IF EXISTS rider_performance_analysis;

CREATE VIEW rider_performance_analysis AS
SELECT 
    rider_id,
    order_date,
    rider_age,
    COUNT(*) as total_orders,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rating,
    SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) as on_time_orders,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    ROUND(AVG(COALESCE(multi_delivery, 1)), 2) as avg_multi_delivery,
    ROUND(
        (AVG(rider_rating) * 25 + 
         (GREATEST(0, 45 - AVG(delivery_time))) * 1.5 + 
         (SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) * 0.5), 
        2
    ) as performance_score,
    MAX(vehicle_type) as primary_vehicle_type
FROM mysql_ready
WHERE rider_id IS NOT NULL 
  AND delivery_time IS NOT NULL 
  AND rider_rating IS NOT NULL
GROUP BY rider_id, order_date, rider_age
ORDER BY order_date, performance_score DESC;


-- 5. 外部因素影响分析表
-- ================================
CREATE VIEW external_factors_analysis AS
SELECT 
    weather,
    traffic_density,
    order_date,
    COUNT(*) as orders,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rating,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    
    -- 与正常天气的对比
    ROUND(AVG(delivery_time) - (
        SELECT AVG(delivery_time) 
        FROM mysql_ready 
        WHERE weather = 'Sunny' AND traffic_density = 'Low'
    ), 2) as time_impact_vs_ideal,
    
    -- 车辆类型适应性
    ROUND(SUM(CASE WHEN vehicle_type = 'Motorcycle' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as motorcycle_usage_rate
FROM mysql_ready
GROUP BY weather, traffic_density, order_date
ORDER BY order_date, avg_delivery_time DESC;

-- 6. 异常订单监控表
-- ================================
CREATE VIEW anomaly_monitoring AS
SELECT 
    order_date,
    -- 超时订单分析
    SUM(CASE WHEN delivery_time > 60 THEN 1 ELSE 0 END) as severe_delays,
    SUM(CASE WHEN delivery_time > 45 THEN 1 ELSE 0 END) as moderate_delays,
    ROUND(SUM(CASE WHEN delivery_time > 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as severe_delay_rate,
    
    -- 低评分订单分析
    SUM(CASE WHEN rider_rating < 3.0 THEN 1 ELSE 0 END) as low_rating_orders,
    ROUND(SUM(CASE WHEN rider_rating < 3.0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as low_rating_rate,
    
    -- 问题骑手识别
    COUNT(DISTINCT CASE WHEN delivery_time > 60 OR rider_rating < 3.0 THEN rider_id END) as problematic_riders,
    
    -- 问题区域识别（城市类型）
    COUNT(DISTINCT CASE WHEN delivery_time > 60 THEN city_type END) as problematic_cities,
    
    -- 问题时段识别
    COUNT(DISTINCT CASE WHEN delivery_time > 60 THEN order_hour END) as problematic_hours
FROM mysql_ready
GROUP BY order_date
ORDER BY order_date;

-- 7. 综合运营指标汇总表（供Tableau使用）
-- ================================
CREATE VIEW operations_summary_for_tableau AS
SELECT 
    order_date,
    city_type,
    time_period,
    weather,
    traffic_density,
    is_festival,
    COUNT(*) as order_volume,
    COUNT(DISTINCT rider_id) as rider_count,
    ROUND(AVG(delivery_time), 2) as avg_delivery_time,
    ROUND(AVG(rider_rating), 2) as avg_rating,
    ROUND(SUM(CASE WHEN delivery_time <= 30 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_rate,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT rider_id), 2) as orders_per_rider,
    order_type,
    vehicle_type,
    ROUND(AVG(COALESCE(multi_delivery, 0)), 2) as avg_multi_delivery
FROM mysql_ready
LEFT JOIN (
    SELECT DISTINCT order_hour,
    CASE 
        WHEN order_hour BETWEEN 6 AND 10 THEN '早餐时段'
        WHEN order_hour BETWEEN 11 AND 14 THEN '午餐时段'
        WHEN order_hour BETWEEN 17 AND 21 THEN '晚餐时段'
        ELSE '非高峰时段'
    END as time_period
    FROM mysql_ready
    WHERE order_hour IS NOT NULL
) time_mapping ON mysql_ready.order_hour = time_mapping.order_hour
GROUP BY 
    order_date, city_type, time_period, weather, traffic_density, 
    is_festival, order_type, vehicle_type
ORDER BY order_date, order_volume DESC;

-- 检查关键指标是否合理
SELECT * FROM daily_operations_kpi LIMIT 5;
SELECT * FROM city_performance_analysis LIMIT 5;