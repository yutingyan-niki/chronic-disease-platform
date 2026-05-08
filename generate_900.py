import pandas as pd
import random
from datetime import datetime, timedelta

# 读取问卷数据
df_q = pd.read_excel("wenjuan.xlsx")
print(f"读取问卷数据：{len(df_q)}人")

# 定义函数
def get_disease_type(row):
    disease = row.get("23、 经医生确诊的慢性病（可多选）：", "")
    if pd.isna(disease):
        return "无"
    d = str(disease)
    if "高血压" in d and "糖尿病" in d:
        return "两者均有"
    elif "高血压" in d:
        return "高血压"
    elif "糖尿病" in d or "2型糖尿病" in d:
        return "糖尿病"
    else:
        return "无"

# 生成居民数据
residents = []
for i in range(len(df_q)):
    row = df_q.iloc[i]
    name = row.get("1、受访老人姓名（选填）", "")
    if pd.isna(name) or name == "":
        name = f"居民{i+1}"
    
    age = row.get("5、老人年龄（周岁）", 70)
    if pd.isna(age):
        age = 70
    elif isinstance(age, str):
        age = int(age.replace("岁", ""))
    
    birth_year = 2026 - age
    id_card = f"110101{birth_year}{random.randint(1,12):02d}{random.randint(1,28):02d}{random.randint(1000,9999)}"
    
    residents.append({
        "name": name,
        "id_card": id_card,
        "gender": row.get("4、老人性别", "男"),
        "age": age,
        "phone": f"138{random.randint(10000000,99999999)}",
        "address": row.get("8、所属社区（选填）", "阳光社区"),
        "disease_type": get_disease_type(row)
    })

# 生成900条设备数据（30人 × 30天）
device = []
start_date = datetime(2026, 4, 1)

for i in range(len(df_q)):
    row = df_q.iloc[i]
    id_card = residents[i]["id_card"]
    
    # 基础值
    try:
        base_sys = float(row.get("11、收缩压（高压）", 120))
    except:
        base_sys = 120
    try:
        base_dia = float(row.get("12、舒张压（低压）", 80))
    except:
        base_dia = 80
    try:
        base_bs = float(str(row.get("13、空腹血糖", 5.5)).replace("_", "."))
    except:
        base_bs = 5.5
    
    for day in range(30):
        date = start_date + timedelta(days=day)
        systolic = int(base_sys) + random.randint(-10, 15)
        diastolic = int(base_dia) + random.randint(-8, 10)
        blood_sugar = round(base_bs + random.uniform(-1.0, 1.5), 1)
        
        systolic = max(90, min(200, systolic))
        diastolic = max(50, min(120, diastolic))
        blood_sugar = max(3.5, min(12.0, blood_sugar))
        
        device.append({
            "id_card": id_card,
            "systolic": systolic,
            "diastolic": diastolic,
            "heart_rate": random.randint(65, 95),
            "blood_sugar": blood_sugar,
            "measure_date": date.strftime("%Y-%m-%d"),
            "measure_time": f"{random.randint(6,10):02d}:{random.randint(0,59):02d}"
        })

df_residents = pd.DataFrame(residents)
df_residents.to_excel("community_data_detailed.xlsx", index=False)
print(f"居民数据：{len(df_residents)}条")

df_device = pd.DataFrame(device)
df_device.to_csv("device_data_detailed.csv", index=False, encoding="utf-8-sig")
print(f"设备数据：{len(df_device)}条（30人 × {len(df_device)//len(df_q)}天）")

print("全部生成完毕！")