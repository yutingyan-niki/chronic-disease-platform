import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# 数据库连接
engine = create_engine('mysql+pymysql://root:Yty20041023@localhost:3306/chronic_db')

# 删除旧表
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS residents'))
    conn.execute(text('DROP TABLE IF EXISTS hospital_records'))
    conn.execute(text('DROP TABLE IF EXISTS device_data'))
    conn.commit()
    print("已清空旧数据。")

num_people = 30
num_days = 30
start_date = datetime(2026, 4, 1)

# ================= 1. 居民表 =================
print(f"正在生成 {num_people} 位居民数据...")
residents = []

for i in range(num_people):
    name = f'居民{i+1}'
    age = random.randint(60, 90)
    id_card = f'110101199{i:03d}1234'
    disease_type = random.choice(['高血压', '糖尿病', '两者均有', '无'])
    height = random.randint(150, 180)
    weight = random.randint(50, 85)
    bmi = round(weight / ((height/100) ** 2), 1)

    residents.append({
        'name': name, 'id_card': id_card, 'gender': random.choice(['男', '女']),
        'age': age, 'phone': f'138{random.randint(10000000,99999999)}',
        'address': f'{random.choice(["阳光", "幸福", "和谐", "安康"])}社区{i+1}号楼',
        'disease_type': disease_type,
        'height': height, 'weight': weight, 'bmi': bmi,
        'smoking': random.choice(['从不吸烟', '偶尔吸烟', '经常吸烟']),
        'drinking': random.choice(['从不饮酒', '偶尔饮酒', '经常饮酒']),
        'emergency_contact': f'{name}家属', 'emergency_phone': f'139{random.randint(10000000,99999999)}'
    })

df_res = pd.DataFrame(residents)
df_res.to_sql('residents', con=engine, if_exists='replace', index=False)
print(f"✅ 居民表：{len(df_res)}条")

# ================= 2. 医院表 =================
print("生成医院诊疗数据...")
hospitals = []

for i in range(num_people):
    id_card = f'110101199{i:03d}1234'
    disease_type = residents[i]['disease_type']
    disease_name = disease_type if disease_type != '无' else '体检正常'
    
    hospitals.append({
        'id_card': id_card,
        'disease': disease_name,
        'blood_pressure': f'{random.randint(110,165)}/{random.randint(70,105)}',
        'blood_sugar': round(random.uniform(4.5, 9.8), 1),
        'cholesterol': round(random.uniform(3.5, 6.5), 1),
        'uric_acid': random.randint(300, 520),
        'medication': random.choice(['硝苯地平', '二甲双胍', '厄贝沙坦', '无']),
        'visit_date': f'2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
        'hospital_name': random.choice(['市人民医院', '社区卫生中心']),
        'doctor_advice': '低盐低脂饮食，定期复查'
    })

df_hos = pd.DataFrame(hospitals)
df_hos.to_sql('hospital_records', con=engine, if_exists='replace', index=False)
print(f"✅ 医院表：{len(df_hos)}条")

# ================= 3. 设备表 =================
print("生成智能设备数据...")
device = []

for i in range(num_people):
    id_card = f'110101199{i:03d}1234'
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        device.append({
            'id_card': id_card,
            'systolic': random.randint(110, 165),
            'diastolic': random.randint(70, 105),
            'heart_rate': random.randint(65, 95),
            'blood_sugar': round(random.uniform(5.0, 9.0), 1),
            'blood_oxygen': random.randint(94, 99),
            'sleep_hours': round(random.uniform(5.5, 8.5), 1),
            'steps': random.randint(3000, 12000),
            'measure_date': date.strftime('%Y-%m-%d'),
            'measure_time': f'{random.randint(6,10):02d}:{random.randint(0,59):02d}'
        })

df_dev = pd.DataFrame(device)
df_dev.to_sql('device_data', con=engine, if_exists='replace', index=False)
print(f"✅ 设备表：{len(df_dev)}条（{num_people}人×{num_days}天）")

print("全部完成！")