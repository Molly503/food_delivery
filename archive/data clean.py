# 英文标准化数据清洗脚本
# 统一使用英文字段值，便于国际化分析

import pandas as pd
import numpy as np

print("📊 读取数据...")
df = pd.read_csv('train.csv')
print(f"原始数据: {len(df)} 行")

# 1. 重命名字段
rename_dict = {
    'ID': 'order_id',
    'Delivery_person_ID': 'rider_id',
    'Delivery_person_Age': 'rider_age',
    'Delivery_person_Ratings': 'rider_rating',
    'Restaurant_latitude': 'restaurant_lat',
    'Restaurant_longitude': 'restaurant_lng',
    'Delivery_location_latitude': 'delivery_lat',
    'Delivery_location_longitude': 'delivery_lng',
    'Order_Date': 'order_date',
    'Time_Orderd': 'order_time',
    'Time_Order_picked': 'pickup_time',
    'Weatherconditions': 'weather',
    'Road_traffic_density': 'traffic_density',
    'Vehicle_condition': 'vehicle_condition',
    'Type_of_order': 'order_type',
    'Type_of_vehicle': 'vehicle_type',
    'multiple_deliveries': 'multi_delivery',
    'City': 'city_type',
    'Time_taken(min)': 'delivery_time',
    'Festival': 'is_festival'
}

df = df.rename(columns=rename_dict)
print("✅ 字段重命名完成")

# 2. 清洗配送时间 - 提取数字
print("🧹 清洗配送时间...")
df['delivery_time'] = df['delivery_time'].astype(str).str.extract('(\d+)')
df['delivery_time'] = pd.to_numeric(df['delivery_time'], errors='coerce')

# 3. 清洗年龄 - 安全转换
print("🧹 清洗年龄数据...")
df['rider_age'] = pd.to_numeric(df['rider_age'], errors='coerce')

# 4. 清洗评分 - 安全转换
print("🧹 清洗评分数据...")
df['rider_rating'] = pd.to_numeric(df['rider_rating'], errors='coerce')

# 5. 清洗文本字段
print("🧹 清洗文本字段...")
text_cols = ['weather', 'traffic_density', 'order_type', 'vehicle_type', 'city_type', 'is_festival']
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()

# 6. 标准化天气条件 (保持英文)
print("🌤️ 标准化天气条件...")
def clean_weather(weather_str):
    if pd.isna(weather_str) or str(weather_str).lower() == 'nan':
        return 'Unknown'
    
    weather_clean = str(weather_str).replace('conditions', '').strip()
    
    # 标准化为规范英文
    weather_mapping = {
        'Sunny': 'Sunny',
        'Stormy': 'Stormy', 
        'Cloudy': 'Cloudy',
        'Fog': 'Foggy',
        'Sandstorms': 'Sandstorm',
        'Windy': 'Windy'
    }
    return weather_mapping.get(weather_clean, weather_clean)

df['weather'] = df['weather'].apply(clean_weather)

# 7. 标准化交通密度 (保持英文)
print("🚦 标准化交通密度...")
def clean_traffic(traffic_str):
    if pd.isna(traffic_str) or str(traffic_str).lower() == 'nan':
        return 'Unknown'
    
    traffic_clean = str(traffic_str).strip()
    
    # 标准化为规范英文
    traffic_mapping = {
        'Low': 'Low',
        'Medium': 'Medium', 
        'High': 'High',
        'Jam': 'Heavy'  # Jam -> Heavy (更标准的英文表达)
    }
    return traffic_mapping.get(traffic_clean, traffic_clean)

df['traffic_density'] = df['traffic_density'].apply(clean_traffic)

# 8. 标准化城市类型 (保持英文)
print("🏙️ 标准化城市类型...")
def clean_city_type(city_str):
    if pd.isna(city_str) or str(city_str).lower() == 'nan':
        return 'Unknown'
    
    city_clean = str(city_str).strip()
    
    # 标准化为规范英文
    city_mapping = {
        'Urban': 'Urban',
        'Metropolitian': 'Metropolitan',  # 修正拼写错误
        'Metropolitan': 'Metropolitan',
        'Semi-Urban': 'Semi-Urban'
    }
    return city_mapping.get(city_clean, city_clean)

df['city_type'] = df['city_type'].apply(clean_city_type)

# 9. 标准化订单类型 (保持英文)
print("🍽️ 标准化订单类型...")
def clean_order_type(order_str):
    if pd.isna(order_str) or str(order_str).lower() == 'nan':
        return 'Other'
    
    order_clean = str(order_str).strip()
    
    # 保持英文，去除多余空格
    order_mapping = {
        'Meal': 'Meal',
        'Snack': 'Snack',
        'Drinks': 'Drinks',
        'Buffet': 'Buffet'
    }
    return order_mapping.get(order_clean, order_clean)

df['order_type'] = df['order_type'].apply(clean_order_type)

# 10. 标准化车辆类型 (保持英文)
print("🛵 标准化车辆类型...")
def clean_vehicle_type(vehicle_str):
    if pd.isna(vehicle_str) or str(vehicle_str).lower() == 'nan':
        return 'Other'
    
    vehicle_clean = str(vehicle_str).strip()
    
    # 标准化英文表达
    vehicle_mapping = {
        'motorcycle': 'Motorcycle',
        'scooter': 'Scooter',
        'electric_scooter': 'Electric_Scooter',
        'bicycle': 'Bicycle'
    }
    return vehicle_mapping.get(vehicle_clean, vehicle_clean)

df['vehicle_type'] = df['vehicle_type'].apply(clean_vehicle_type)

# 11. 清洗节日标识
print("🎉 清洗节日标识...")
def clean_festival(festival_str):
    if pd.isna(festival_str) or str(festival_str).lower() == 'nan':
        return 0
    festival_clean = str(festival_str).strip().lower()
    return 1 if festival_clean == 'yes' else 0

df['is_festival'] = df['is_festival'].apply(clean_festival)

# 12. 处理日期格式
print("📅 处理日期格式...")
def clean_date(date_str):
    try:
        if pd.isna(date_str) or str(date_str).lower() == 'nan':
            return np.nan
        # 转换 19-03-2022 -> 2022-03-19
        return pd.to_datetime(date_str, format='%d-%m-%Y').strftime('%Y-%m-%d')
    except:
        return str(date_str)

df['order_date'] = df['order_date'].apply(clean_date)

# 13. 过滤异常数据
print("🔍 过滤异常数据...")
before_count = len(df)

# 删除关键字段为空的行
df = df.dropna(subset=['delivery_time', 'rider_age', 'rider_rating'])

# 过滤数值范围
df = df[
    (df['delivery_time'] >= 5) & (df['delivery_time'] <= 120) &
    (df['rider_age'] >= 18) & (df['rider_age'] <= 65) &
    (df['rider_rating'] >= 1) & (df['rider_rating'] <= 5)
]

print(f"过滤前: {before_count} 行")
print(f"过滤后: {len(df)} 行")
print(f"清理了: {before_count - len(df)} 行异常数据")

# 14. 添加有用的计算字段
print("➕ 添加计算字段...")

# 添加订单小时
try:
    df['order_hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S', errors='coerce').dt.hour
    df['pickup_hour'] = pd.to_datetime(df['pickup_time'], format='%H:%M:%S', errors='coerce').dt.hour
except:
    df['order_hour'] = np.nan
    df['pickup_hour'] = np.nan

# 计算配送距离（简化版哈弗赛因公式）
def calculate_distance(row):
    try:
        if pd.isna(row['restaurant_lat']) or pd.isna(row['delivery_lat']):
            return np.nan
        
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lng1 = radians(row['restaurant_lat']), radians(row['restaurant_lng'])
        lat2, lng2 = radians(row['delivery_lat']), radians(row['delivery_lng'])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        
        return round(c * 6371, 2)  # 地球半径6371km
    except:
        return np.nan

df['distance_km'] = df.apply(calculate_distance, axis=1)

# 计算配送效率 (分钟/公里)
df['efficiency_min_per_km'] = df['delivery_time'] / df['distance_km']
df['efficiency_min_per_km'] = df['efficiency_min_per_km'].replace([np.inf, -np.inf], np.nan)

# 添加时段分类
def categorize_time_period(hour):
    if pd.isna(hour):
        return 'Unknown'
    elif 6 <= hour < 11:
        return 'Morning'
    elif 11 <= hour < 14:
        return 'Lunch'
    elif 14 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Dinner'
    else:
        return 'Late_Night'

df['time_period'] = df['order_hour'].apply(categorize_time_period)

# 15. 保存数据
print("💾 保存清洗后的数据...")
df.to_csv('clean_delivery_data_en.csv', index=False, encoding='utf-8-sig')

# 16. 数据质量报告
print(f"\n📊 数据清洗完成!")
print(f"最终数据: {len(df):,} 行, {len(df.columns)} 列")
print(f"平均配送时间: {df['delivery_time'].mean():.1f} 分钟")
print(f"平均配送距离: {df['distance_km'].mean():.2f} 公里")
print(f"平均骑手年龄: {df['rider_age'].mean():.1f} 岁")
print(f"平均骑手评分: {df['rider_rating'].mean():.2f} 分")

print("\n📋 数据分布概览:")
print("\n🏙️ 城市类型分布:")
print(df['city_type'].value_counts())

print("\n🌤️ 天气条件分布:")
print(df['weather'].value_counts())

print("\n🚦 交通密度分布:")
print(df['traffic_density'].value_counts())

print("\n🍽️ 订单类型分布:")
print(df['order_type'].value_counts())

print("\n🛵 车辆类型分布:")
print(df['vehicle_type'].value_counts())

print("\n⏰ 时段分布:")
print(df['time_period'].value_counts())

print("\n✅ 英文标准化数据已保存为: clean_delivery_data_en.csv")
print("🚀 可以开始分析了!")

# 可选：生成数据字典
data_dict = {
    'order_id': 'Unique order identifier',
    'rider_id': 'Delivery person identifier', 
    'rider_age': 'Delivery person age',
    'rider_rating': 'Delivery person rating (1-5)',
    'restaurant_lat': 'Restaurant latitude',
    'restaurant_lng': 'Restaurant longitude',
    'delivery_lat': 'Delivery location latitude', 
    'delivery_lng': 'Delivery location longitude',
    'order_date': 'Order date (YYYY-MM-DD)',
    'order_time': 'Order time (HH:MM:SS)',
    'pickup_time': 'Pickup time (HH:MM:SS)',
    'weather': 'Weather condition (Sunny/Stormy/Cloudy/Foggy/Sandstorm/Windy)',
    'traffic_density': 'Traffic density (Low/Medium/High/Heavy)',
    'vehicle_condition': 'Vehicle condition score',
    'order_type': 'Type of order (Meal/Snack/Drinks/Buffet)',
    'vehicle_type': 'Vehicle type (Motorcycle/Scooter/Electric_Scooter/Bicycle)',
    'multi_delivery': 'Multiple deliveries flag (0/1)',
    'city_type': 'City type (Urban/Metropolitan/Semi-Urban)',
    'delivery_time': 'Delivery duration in minutes',
    'is_festival': 'Festival period flag (0/1)',
    'order_hour': 'Hour of order (0-23)',
    'pickup_hour': 'Hour of pickup (0-23)',
    'distance_km': 'Delivery distance in kilometers',
    'efficiency_min_per_km': 'Delivery efficiency (minutes per km)',
    'time_period': 'Time period (Morning/Lunch/Afternoon/Dinner/Late_Night)'
}

dict_df = pd.DataFrame(list(data_dict.items()), columns=['Field', 'Description'])
dict_df.to_csv('data_dictionary_en.csv', index=False)
print("📚 数据字典已保存为: data_dictionary_en.csv")