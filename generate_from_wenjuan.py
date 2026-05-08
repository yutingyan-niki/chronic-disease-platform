import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# 读取问卷数据
df_q = pd.read_excel("wenjuan.xlsx")
print(f"读取问卷：{len(df_q)}人")

# 数据库连接
engine = create_engine('mysql+pymysql://root:Yty20041023@localhost:3306/chronic_db')

# 删除旧表
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS residents'))
    conn.execute(text('DROP TABLE IF EXISTS hospital_records'))
    conn.execute(text('DROP TABLE IF EXISTS device_data'))
    conn.commit()
    print("已清空旧数据。")

# ================= 1. 生成居民表（使用问卷真实数据） =================
residents = []
num_days = 30
start_date = datetime(2026, 4, 1)

for i in range(len(df_q)):
    row = df_q.iloc[i]
    
    # 真实姓名
    name = row.get("1、受访老人姓名（选填）", "")
    if pd.isna(name) or name == "":
        name = f"居民{i+1}"
    
    # 真实年龄
    age = row.get("5、老人年龄（周岁）", 70)
    if pd.isna(age):
        age = 70
    elif isinstance(age, str):
        age = int(age.replace("岁", ""))
    
    # 真实性别
    gender = row.get("4、老人性别", "男")
    
    # 真实地址
    address = row.get("8、所属社区（选填）", "")
    if pd.isna(address) or address == "":
        address = f"阳光社区{i+1}号楼"
    
    # 真实慢性病
    disease_raw = row.get("23、 经医生确诊的慢性病（可多选）：", "")
    disease_str = str(disease_raw) if not pd.isna(disease_raw) else ""
    if "高血压" in disease_str and "糖尿病" in disease_str:
        disease_type = "两者均有"
    elif "高血压" in disease_str:
        disease_type = "高血压"
    elif "糖尿病" in disease_str or "2型糖尿病" in disease_str:
        disease_type = "糖尿病"
    else:
        disease_type = "无"
    
    # 生成身份证号（基于序号，保证唯一）
    id_card = f'110101199{i:03d}1234'
    
    # 真实身高体重（如果有）
    height = row.get("9、身高（cm）", 0)
    if pd.isna(height) or height == 0:
        height = random.randint(150, 175)
    else:
        try:
            height = int(height)
        except:
            height = 165
    
    weight = row.get("10、体重（kg）", 0)
    if pd.isna(weight) or weight == 0:
        weight = random.randint(50, 75)
    else:
        try:
            weight = int(weight)
        except:
            weight = 65
    
    bmi = round(weight / ((height/100) ** 2), 1)
    
    residents.append({
        'name': name,
        'id_card': id_card,
        'gender': gender,
        'age': age,
        'phone': f'138{random.randint(10000000,99999999)}',
        'address': address,
        'disease_type': disease_type,
        'height': height,
        'weight': weight,
        'bmi': bmi,
        'smoking': row.get("17、吸烟情况：", "从不吸烟"),
        'drinking': row.get("18、饮酒情况：", "从不饮酒"),
        'emergency_contact': f'{name}家属',
        'emergency_phone': f'139{random.randint(10000000,99999999)}'
    })

df_res = pd.DataFrame(residents)
df_res.to_sql('residents', con=engine, if_exists='replace', index=False)
print(f"✅ 居民表：{len(df_res)}条（姓名、年龄、疾病均来自问卷）")

# ================= 2. 生成医院表（基于真实疾病） =================
hospitals = []

for i in range(len(df_q)):
    id_card = residents[i]['id_card']
    disease_type = residents[i]['disease_type']
    disease_name = disease_type if disease_type != '无' else '体检正常'
    
    # 真实血压血糖值
    bp_high = df_q.iloc[i].get("11、收缩压（高压）", 120)
    bp_low = df_q.iloc[i].get("12、舒张压（低压）", 80)
    blood_sugar = df_q.iloc[i].get("13、空腹血糖", 5.5)
    
    hospitals.append({
        'id_card': id_card,
        'disease': disease_name,
        'blood_pressure': f'{bp_high}/{bp_low}',
        'blood_sugar': blood_sugar if not pd.isna(blood_sugar) else 5.5,
        'cholesterol': round(random.uniform(3.5, 6.5), 1),
        'uric_acid': random.randint(300, 520),
        'medication': random.choice(['硝苯地平', '二甲双胍', '厄贝沙坦', '无']),
        'visit_date': f'2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
        'hospital_name': df_q.iloc[i].get("30、患病首选就诊：", "社区卫生服务中心"),
        'doctor_advice': '低盐低脂饮食，定期复查'
    })

df_hos = pd.DataFrame(hospitals)
df_hos.to_sql('hospital_records', con=engine, if_exists='replace', index=False)
print(f"✅ 医院表：{len(df_hos)}条（基于真实疾病）")

# ================= 3. 生成设备表（基于真实血压血糖值） =================
device = []

for i in range(len(df_q)):
    id_card = residents[i]['id_card']
    
    # 基于问卷真实值作为基准
    base_sys = df_q.iloc[i].get("11、收缩压（高压）", 120)
    base_dia = df_q.iloc[i].get("12、舒张压（低压）", 80)
    base_bs = df_q.iloc[i].get("13、空腹血糖", 5.5)
    
    try:
        base_sys = float(base_sys)
    except:
        base_sys = 120
    try:
        base_dia = float(base_dia)
    except:
        base_dia = 80
    try:
        base_bs = float(base_bs)
    except:
        base_bs = 5.5
    
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        device.append({
            'id_card': id_card,
            'systolic': max(90, min(200, int(base_sys) + random.randint(-12, 18))),
            'diastolic': max(55, min(120, int(base_dia) + random.randint(-10, 12))),
            'heart_rate': random.randint(65, 95),
            'blood_sugar': round(max(3.5, min(12.0, base_bs + random.uniform(-1.2, 1.8))), 1),
            'blood_oxygen': random.randint(94, 99),
            'sleep_hours': round(random.uniform(5.5, 8.5), 1),
            'steps': random.randint(3000, 12000),
            'measure_date': date.strftime('%Y-%m-%d'),
            'measure_time': f'{random.randint(6,10):02d}:{random.randint(0,59):02d}'
        })

df_dev = pd.DataFrame(device)
df_dev.to_sql('device_data', con=engine, if_exists='replace', index=False)
print(f"✅ 设备表：{len(df_dev)}条（{len(df_q)}人×{num_days}天，基于真实血压血糖）")

print("\n🎉 全部完成！")
print("数据说明：")
print("  - 居民表：使用问卷真实姓名、年龄、性别、地址、慢性病")
print("  - 医院表：基于真实慢性病生成")
print("  - 设备表：基于真实血压/血糖值生成30天连续数据")