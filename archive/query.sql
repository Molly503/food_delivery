SELECT * FROM food_delivery.train;

-- 1. 配送效率核心指标 
SELECT 
    TRIM(City) as city_type,
    ROUND(AVG(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)), 2) as avg_delivery_time,
    COUNT(*) as order_count,
    MIN(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)) as min_delivery_time,
    MAX(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)) as max_delivery_time,
    ROUND(STDDEV(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)), 2) as std_delivery_time
FROM train   
WHERE 
    `Time_taken(min)` IS NOT NULL 
    AND CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED) > 0 
    AND CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED) < 120
GROUP BY TRIM(City)
ORDER BY avg_delivery_time;

-- 2. 影响配送时间的关键因素分析
-- 天气 + 交通密度 + 车辆类型对配送时间的综合影响
SELECT 
    TRIM(REPLACE(Weatherconditions, 'conditions', '')) as weather_condition,
    TRIM(Road_traffic_density) as traffic_density,
    TRIM(Type_of_vehicle) as vehicle_type,
    ROUND(AVG(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)), 2) as avg_delivery_time,
    COUNT(*) as order_volume,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating,
    -- 计算相对于总体平均的差异
    ROUND(AVG(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)) - 
          (SELECT AVG(CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED)) 
           FROM train WHERE `Time_taken(min)` IS NOT NULL), 2) as time_difference_vs_avg
FROM train
WHERE 
    `Time_taken(min)` IS NOT NULL 
    AND Weatherconditions IS NOT NULL
    AND Road_traffic_density IS NOT NULL
    AND Type_of_vehicle IS NOT NULL
    AND CAST(REPLACE(REPLACE(`Time_taken(min)`, '(min)', ''), ' ', '') AS UNSIGNED) BETWEEN 5 AND 100
GROUP BY 
    TRIM(REPLACE(Weatherconditions, 'conditions', '')), 
    TRIM(Road_traffic_density), 
    TRIM(Type_of_vehicle)
HAVING COUNT(*) >= 20  -- 只显示样本量足够的组合
ORDER BY avg_delivery_time DESC
LIMIT 20;