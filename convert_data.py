import pandas as pd
import sys

# 读取问卷数据
df = pd.read_excel("wenjuan.xlsx")
print("成功读取数据，共", len(df), "条记录")

# ==================== 1. 生成社区普查数据 ====================
residents_list = []

for i in range(len(df)):
    row = df.iloc[i]
    
    name = row.get("1、受访老人姓名（选填）", "")
    if pd.isna(name) or name == "":
        name = f"居民{i+1}"
    
    age = row.get("5、老人年龄（周岁）", 70)
    if pd.isna(age):
        age = 70
    elif isinstance(age, str):
        age = age.replace("岁", "").strip()
        try:
            age = int(age)
        except:
            age = 70
    
    disease = row.get("23、 经医生确诊的慢性病（可多选）：", "")
    if pd.isna(disease):
        disease_type = "无"
    else:
        disease_str = str(disease)
        if "高血压" in disease_str and "糖尿病" in disease_str:
            disease_type = "两者均有"
        elif "高血压" in disease_str:
            disease_type = "高血压"
        elif "糖尿病" in disease_str or "2型糖尿病" in disease_str:
            disease_type = "糖尿病"
        else:
            disease_type = "无"
    
    residents_list.append({
        "name": name,
        "id_card": f"110101199{i:03d}1234",
        "gender": row.get("4、老人性别", ""),
        "age": age,
        "phone": f"1380000{i:04d}",
        "address": row.get("8、所属社区（选填）", ""),
        "disease_type": disease_type
    })

df_residents = pd.DataFrame(residents_list)
df_residents.to_excel("community_data.xlsx", index=False)
print(f"生成 community_data.xlsx（{len(df_residents)}条）")

# ==================== 2. 生成医院诊疗数据 ====================
hospital_list = []

for i in range(len(df)):
    row = df.iloc[i]
    
    disease = row.get("23、 经医生确诊的慢性病（可多选）：", "")
    if pd.isna(disease):
        continue
    
    # 处理血压值
    bp_high = row.get("11、收缩压（高压）", "")
    bp_low = row.get("12、舒张压（低压）", "")
    
    # 如果血压值是文字（如"正常"），替换为空
    if isinstance(bp_high, str) and not bp_high.isdigit():
        bp_high = ""
    if isinstance(bp_low, str) and not bp_low.isdigit():
        bp_low = ""
    
    hospital_list.append({
        "id_card": f"110101199{i:03d}1234",
        "disease": str(disease),
        "blood_pressure": f"{bp_high}/{bp_low}" if bp_high and bp_low else "",
        "blood_sugar": row.get("13、空腹血糖", ""),
        "visit_date": "2025-10-15",
        "hospital_name": row.get("30、患病首选就诊：", ""),
        "doctor_advice": "定期复查，按时服药"
    })

df_hospital = pd.DataFrame(hospital_list)
df_hospital.to_excel("hospital_data.xlsx", index=False)
print(f"生成 hospital_data.xlsx（{len(hospital_list)}条）")

# ==================== 3. 生成智能设备数据 ====================
device_list = []

for i in range(len(df)):
    row = df.iloc[i]
    
    systolic = row.get("11、收缩压（高压）", "")
    diastolic = row.get("12、舒张压（低压）", "")
    
    # 跳过非数字的血压值
    try:
        systolic_val = int(systolic) if str(systolic).isdigit() else None
        diastolic_val = int(diastolic) if str(diastolic).isdigit() else None
    except:
        systolic_val = None
        diastolic_val = None
    
    if systolic_val is None or diastolic_val is None:
        continue
    
    device_list.append({
        "id_card": f"110101199{i:03d}1234",
        "systolic": systolic_val,
        "diastolic": diastolic_val,
        "heart_rate": row.get("15、心率（次/分钟）", 70),
        "blood_sugar": row.get("13、空腹血糖", 5.5),
        "measure_date": "2026-05-01",
        "measure_time": "08:30"
    })

df_device = pd.DataFrame(device_list)
df_device.to_csv("device_data.csv", index=False, encoding="utf-8-sig")
print(f"生成 device_data.csv（{len(device_list)}条）")

print("\n所有文件生成完毕！")