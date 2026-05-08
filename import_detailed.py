import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:Yty20041023@localhost:3306/chronic_db')

print("读取详细数据...")
df_residents = pd.read_excel("community_data_detailed.xlsx")
df_hospital = pd.read_excel("hospital_data_detailed.xlsx")
df_device = pd.read_csv("device_data_detailed.csv")

print(f"居民表：{len(df_residents)}条")
print(f"医院表：{len(df_hospital)}条")
print(f"设备表：{len(df_device)}条")

print("导入居民表...")
df_residents.to_sql('residents', con=engine, if_exists='replace', index=False)

print("导入医院表...")
df_hospital.to_sql('hospital_records', con=engine, if_exists='replace', index=False)

print("导入设备表...")
df_device.to_sql('device_data', con=engine, if_exists='replace', index=False)

print("全部导入成功！")