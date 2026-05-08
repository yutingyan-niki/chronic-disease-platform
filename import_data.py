import pandas as pd
import pymysql
from sqlalchemy import create_engine

# 连接数据库（注意密码写在这里）
engine = create_engine('mysql+pymysql://root:Yty20041023@localhost:3306/chronic_db')

# 测试连接
try:
    with engine.connect() as conn:
        print("数据库连接成功！")
except Exception as e:
    print("连接失败：", e)
    exit()

# 读取数据文件
df_residents = pd.read_excel("community_data.xlsx")
df_hospital = pd.read_excel("hospital_data.xlsx")
df_device = pd.read_csv("device_data.csv")

print(f"居民数据：{len(df_residents)}条")
print(f"医院数据：{len(df_hospital)}条")
print(f"设备数据：{len(df_device)}条")

# 导入到数据库
df_residents.to_sql('residents', con=engine, if_exists='replace', index=False)
df_hospital.to_sql('hospital_records', con=engine, if_exists='replace', index=False)
df_device.to_sql('device_data', con=engine, if_exists='replace', index=False)

print("数据导入成功！")