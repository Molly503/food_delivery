# 简化版MySQL兼容清洗脚本
# 兼容任何pandas版本

import pandas as pd
import numpy as np

print("📊 读取原始数据...")
df = pd.read_csv('train.csv')
print(f"原始数据: {len(df)} 行")

# 1. 字段重命名
print("✏️ 重命名字段...")
df = df.rename(columns={
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
})

# 2. 清洗核心字段
print("🧹 清洗数据...")

# 配送时间：提取数字
df['delivery_time'] = df['delivery_time'].astype(str).str.extract('(\d+)')
df['delivery_time'] = pd.to_numeric(df['delivery_time'], errors='coerce')

# 年龄和评分
df['rider_age'] = pd.to_numeric(df['rider_age'], errors='coerce')
df['rider_rating'] = pd.to_numeric(df['rider_rating'], errors='coerce')

# 经纬度
df['restaurant_lat'] = pd.to_numeric(df['restaurant_lat'], errors='coerce')
df['restaurant_lng'] = pd.to_numeric(df['restaurant_lng'], errors='coerce')
df['delivery_lat'] = pd.to_numeric(df['delivery_lat'], errors='coerce')
df['delivery_lng'] = pd.to_numeric(df['delivery_lng'], errors='coerce')

# 多重配送
df['multi_delivery'] = df['multi_delivery'].replace(['NaN', 'NaN ', 'nan'], np.nan)
df['multi_delivery'] = pd.to_numeric(df['multi_delivery'], errors='coerce')

# 3. 清洗文本字段
print("📝 处理文本字段...")

# 去除空格和特殊字符
text_cols = ['rider_id', 'weather', 'traffic_density', 'order_type', 'vehicle_type', 'city_type']
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()

# 标准化值
# 天气
df['weather'] = df['weather'].str.replace('conditions', '').str.strip()
df['weather'] = df['weather'].replace({
    'Sunny': 'Sunny', 'Stormy': 'Stormy', 'Cloudy': 'Cloudy',
    'Fog': 'Foggy', 'Sandstorms': 'Sandstorm', 'Windy': 'Windy'
})
df['weather'] = df['weather'].fillna('Unknown')

# 交通
df['traffic_density'] = df['traffic_density'].replace({
    'Low': 'Low', 'Medium': 'Medium', 'High': 'High', 'Jam': 'Heavy'
})
df['traffic_density'] = df['traffic_density'].fillna('Unknown')

# 城市
df['city_type'] = df['city_type'].replace({
    'Urban': 'Urban', 'Metropolitian': 'Metropolitan', 
    'Metropolitan': 'Metropolitan', 'Semi-Urban': 'Semi_Urban'
})
df['city_type'] = df['city_type'].fillna('Unknown')

# 订单类型
df['order_type'] = df['order_type'].replace({
    'Meal': 'Meal', 'Snack': 'Snack', 'Drinks': 'Drinks', 'Buffet': 'Buffet'
})
df['order_type'] = df['order_type'].fillna('Other')

# 车辆类型
df['vehicle_type'] = df['vehicle_type'].replace({
    'motorcycle': 'Motorcycle', 'scooter': 'Scooter',
    'electric_scooter': 'Electric_Scooter', 'bicycle': 'Bicycle'
})
df['vehicle_type'] = df['vehicle_type'].fillna('Other')

# 节日
df['is_festival'] = (df['is_festival'].astype(str).str.strip() == 'Yes').astype(int)

# 4. 过滤异常数据 - 兼容老版本pandas
print("🔍 过滤异常数据...")
before_count = len(df)

# 逐步过滤，避免版本兼容性问题
# 过滤配送时间
valid_delivery = (df['delivery_time'] >= 5) & (df['delivery_time'] <= 120)
valid_delivery = valid_delivery.fillna(False)

# 过滤年龄
valid_age = (df['rider_age'] >= 18) & (df['rider_age'] <= 65)
valid_age = valid_age.fillna(False)

# 过滤评分
valid_rating = (df['rider_rating'] >= 1) & (df['rider_rating'] <= 5)
valid_rating = valid_rating.fillna(False)

# 组合过滤条件
df = df[valid_delivery & valid_age & valid_rating].copy()

print(f"过滤前: {before_count} 行")
print(f"过滤后: {len(df)} 行")

# 5. 添加时间字段
print("⏰ 添加时间字段...")
try:
    df['order_hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S', errors='coerce').dt.hour
except:
    df['order_hour'] = np.nan

# 6. 处理空值 - MySQL友好方式
print("🔧 处理空值...")

# 数值字段保留NaN
numeric_cols = ['delivery_time', 'rider_age', 'rider_rating', 'restaurant_lat', 
                'restaurant_lng', 'delivery_lat', 'delivery_lng', 'vehicle_condition',
                'multi_delivery', 'order_hour']

# 文本字段用空字符串替换NaN
text_cols = ['rider_id', 'weather', 'traffic_density', 'order_type', 
             'vehicle_type', 'city_type', 'order_time', 'pickup_time']

for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna('')

# 日期字段特殊处理
if 'order_date' in df.columns:
    try:
        df['order_date'] = pd.to_datetime(df['order_date'], format='%d-%m-%Y', errors='coerce')
        df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d')
        df['order_date'] = df['order_date'].fillna('')
    except:
        df['order_date'] = df['order_date'].fillna('')

# 7. 保存MySQL兼容文件
print("💾 保存MySQL兼容文件...")
df.to_csv('mysql_ready.csv', 
          index=False, 
          encoding='utf-8',    # 标准UTF-8，无BOM
          na_rep='NULL')       # MySQL友好的空值表示

print(f"\n✅ 处理完成!")
print(f"📊 最终数据: {len(df):,} 行, {len(df.columns)} 列")
print(f"💾 文件: mysql_ready.csv")

# 8. 生成简单的建表语句
print("\n📄 生成建表语句...")
create_sql = """CREATE TABLE delivery_data (
    order_id VARCHAR(50),
    rider_id VARCHAR(50),
    rider_age INT,
    rider_rating DECIMAL(3,2),
    restaurant_lat DECIMAL(10,6),
    restaurant_lng DECIMAL(10,6),
    delivery_lat DECIMAL(10,6),
    delivery_lng DECIMAL(10,6),
    order_date DATE,
    order_time VARCHAR(20),
    pickup_time VARCHAR(20),
    weather VARCHAR(20),
    traffic_density VARCHAR(20),
    vehicle_condition INT,
    order_type VARCHAR(20),
    vehicle_type VARCHAR(30),
    multi_delivery INT,
    city_type VARCHAR(20),
    delivery_time INT,
    is_festival TINYINT,
    order_hour INT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""

with open('create_table_simple.sql', 'w') as f:
    f.write(create_sql)

print("📄 建表语句: create_table_simple.sql")

# 9. 数据概览
print(f"\n📊 数据概览:")
print(f"- 平均配送时间: {df['delivery_time'].mean():.1f} 分钟")
print(f"- 平均骑手年龄: {df['rider_age'].mean():.1f} 岁")
print(f"- 平均骑手评分: {df['rider_rating'].mean():.2f} 分")

print("\n🎉 可以导入MySQL了!")
print("\n📋 导入步骤:")
print("1. mysql> source create_table_simple.sql")
print("2. mysql> LOAD DATA INFILE 'mysql_ready.csv' INTO TABLE delivery_data")
print("   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"'")
print("   LINES TERMINATED BY '\\n' IGNORE 1 ROWS;")