import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# 连接 MySQL
mysql_engine = create_engine('mysql+pymysql://root:Yty20041023@localhost:3306/chronic_db')

# 连接 SQLite
sqlite_conn = sqlite3.connect('chronic.db')

# 读取 MySQL 数据
print("正在读取 MySQL 数据...")
df_res = pd.read_sql("SELECT * FROM residents", mysql_engine)
df_hos = pd.read_sql("SELECT * FROM hospital_records", mysql_engine)
df_dev = pd.read_sql("SELECT * FROM device_data", mysql_engine)

print(f"居民表：{len(df_res)} 条")
print(f"医院表：{len(df_hos)} 条")
print(f"设备表：{len(df_dev)} 条")

# 写入 SQLite
print("正在写入 SQLite...")
df_res.to_sql('residents', sqlite_conn, if_exists='replace', index=False)
df_hos.to_sql('hospital_records', sqlite_conn, if_exists='replace', index=False)
df_dev.to_sql('device_data', sqlite_conn, if_exists='replace', index=False)

print("迁移完成！")