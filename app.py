import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(page_title="社区智慧慢病管理平台", layout="wide")
st.title("🏥 社区智慧慢性病管理平台")

# SQLite 数据库连接（自动创建 chronic.db 文件）
@st.cache_resource
def get_connection():
    return sqlite3.connect('chronic.db', check_same_thread=False)

conn = get_connection()

# 初始化数据库表（如果不存在则创建）
def init_db():
    cursor = conn.cursor()
    
    # 居民表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            id_card TEXT UNIQUE,
            gender TEXT,
            age INTEGER,
            phone TEXT,
            address TEXT,
            disease_type TEXT,
            height REAL,
            weight REAL,
            bmi REAL,
            smoking TEXT,
            drinking TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT
        )
    ''')
    
    # 医院诊疗记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospital_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_card TEXT,
            disease TEXT,
            blood_pressure TEXT,
            blood_sugar REAL,
            cholesterol REAL,
            uric_acid INTEGER,
            medication TEXT,
            visit_date TEXT,
            department TEXT,
            hospital_name TEXT,
            doctor_advice TEXT,
            next_visit_date TEXT
        )
    ''')
    
    # 设备监测数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_data (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_card TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            heart_rate INTEGER,
            blood_sugar REAL,
            blood_oxygen INTEGER,
            sleep_hours REAL,
            steps INTEGER,
            weight REAL,
            measure_date TEXT,
            measure_time TEXT
        )
    ''')
    
    conn.commit()

init_db()

# 辅助函数：执行SQL并返回DataFrame
def read_sql(query):
    return pd.read_sql_query(query, conn)

# 侧边栏导航
menu = st.sidebar.selectbox("功能导航",
    ["数据浏览", "档案管理", "关联查询", "预警提示", "可视化分析"])

# ==================== 数据浏览模块 ====================
if menu == "数据浏览":
    st.subheader("📋 居民健康档案列表（社区普查+诊疗+设备数据）")
    
    try:
        df_res = read_sql("SELECT * FROM residents")
        df_hos = read_sql("SELECT * FROM hospital_records")
        df_dev = read_sql("SELECT id_card, systolic, diastolic, blood_sugar, measure_date FROM device_data")
        
        df = df_res.merge(df_hos, on="id_card", how="left").merge(df_dev, on="id_card", how="left")
        
        st.markdown("##### 🔍 筛选条件")
        col1, col2, col3 = st.columns(3)
        with col1:
            name_search = st.text_input("姓名", placeholder="输入姓名搜索")
        with col2:
            disease_search = st.selectbox("疾病类型", ["全部", "高血压", "糖尿病", "两者均有", "无"])
        with col3:
            age_min, age_max = st.slider("年龄范围", 0, 120, (0, 120))
        
        if name_search:
            df = df[df["name"].str.contains(name_search, na=False)]
        if disease_search != "全部":
            df = df[df["disease_type"] == disease_search]
        df = df[(df["age"] >= age_min) & (df["age"] <= age_max)]
        
        sort_col = st.selectbox("排序字段", ["name", "age", "measure_date"])
        df = df.sort_values(by=sort_col, ascending=True)
        
        page_size = 10
        total_page = max(1, (len(df) + page_size - 1) // page_size)
        page = st.number_input("页码", min_value=1, max_value=total_page, value=1)
        start = (page - 1) * page_size
        end = start + page_size
        df_page = df.iloc[start:end]
        
        st.dataframe(df_page, use_container_width=True)
        st.caption(f"第 {page}/{total_page} 页｜共 {len(df)} 条记录｜每页 {page_size} 条")
    except Exception as e:
        st.info(f"暂无数据或加载失败：{e}")

# ==================== 档案管理模块 ====================
elif menu == "档案管理":
    st.subheader("📝 健康档案管理")
    
    st.markdown("##### 🔍 档案快速筛选")
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        search_name = st.text_input("按姓名筛选", placeholder="输入姓名")
    with col_search2:
        search_disease = st.selectbox("按疾病类型筛选", ["全部", "高血压", "糖尿病", "两者均有", "无"])
    
    df_all = read_sql("SELECT * FROM residents")
    if search_name:
        df_all = df_all[df_all["name"].str.contains(search_name, na=False)]
    if search_disease != "全部":
        df_all = df_all[df_all["disease_type"] == search_disease]
    st.dataframe(df_all, use_container_width=True)
    st.caption(f"筛选结果：共 {len(df_all)} 条记录")
    
    tab1, tab2, tab3, tab4 = st.tabs(["新增档案", "修改档案", "删除档案", "批量导入Excel/CSV"])
    
    # 新增档案
    with tab1:
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("姓名")
                id_card = st.text_input("身份证号")
                gender = st.selectbox("性别", ["男", "女"])
                age = st.number_input("年龄", min_value=0, max_value=120, step=1)
                phone = st.text_input("联系电话")
                address = st.text_input("居住地址")
            with col2:
                height = st.number_input("身高(cm)", min_value=100, max_value=250, step=1, value=165)
                weight = st.number_input("体重(kg)", min_value=30, max_value=200, step=1, value=65)
                smoking = st.selectbox("吸烟情况", ["从不吸烟", "偶尔吸烟", "经常吸烟", "已戒烟"])
                drinking = st.selectbox("饮酒情况", ["从不饮酒", "偶尔饮酒", "经常饮酒"])
                emergency_contact = st.text_input("紧急联系人")
                emergency_phone = st.text_input("紧急联系电话")
            
            disease_type = st.selectbox("慢性病类型", ["高血压", "糖尿病", "两者均有", "无"])
            
            if st.form_submit_button("新增居民"):
                if not name or not id_card:
                    st.warning("请填写姓名和身份证号")
                else:
                    try:
                        bmi = round(weight / ((height/100) ** 2), 1) if height and weight else None
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO residents (name, id_card, gender, age, phone, address, disease_type, height, weight, bmi, smoking, drinking, emergency_contact, emergency_phone)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (name, id_card, gender, age, phone, address, disease_type, height, weight, bmi, smoking, drinking, emergency_contact, emergency_phone))
                        conn.commit()
                        st.success("新增成功！")
                    except Exception as e:
                        st.error(f"新增失败：{e}")
    
    # 修改档案
    with tab2:
        st.subheader("修改居民信息")
        search_id = st.text_input("输入要修改的居民身份证号", key="search_id")
        if st.button("查询居民", key="search_btn"):
            try:
                df = read_sql(f"SELECT * FROM residents WHERE id_card = '{search_id}'")
                if not df.empty:
                    st.session_state["edit_data"] = df.iloc[0].to_dict()
                    st.success(f"找到居民：{df.iloc[0]['name']}")
                else:
                    st.error("未找到该居民")
            except Exception as e:
                st.error(f"查询失败：{e}")
        
        if "edit_data" in st.session_state:
            old = st.session_state["edit_data"]
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("姓名", value=old.get("name", ""))
                    new_gender = st.selectbox("性别", ["男", "女"], index=0 if old.get("gender") == "男" else 1)
                    new_age = st.number_input("年龄", min_value=0, max_value=120, value=int(old.get("age", 0)))
                    new_phone = st.text_input("联系电话", value=old.get("phone", ""))
                    new_address = st.text_input("居住地址", value=old.get("address", ""))
                with col2:
                    new_height = st.number_input("身高(cm)", value=int(old.get("height", 165)))
                    new_weight = st.number_input("体重(kg)", value=int(old.get("weight", 65)))
                    new_smoking = st.selectbox("吸烟情况", ["从不吸烟", "偶尔吸烟", "经常吸烟", "已戒烟"],
                                               index=["从不吸烟","偶尔吸烟","经常吸烟","已戒烟"].index(old.get("smoking", "从不吸烟")))
                    new_drinking = st.selectbox("饮酒情况", ["从不饮酒", "偶尔饮酒", "经常饮酒"],
                                                index=["从不饮酒","偶尔饮酒","经常饮酒"].index(old.get("drinking", "从不饮酒")))
                    new_emergency = st.text_input("紧急联系人", value=old.get("emergency_contact", ""))
                    new_emergency_phone = st.text_input("紧急联系电话", value=old.get("emergency_phone", ""))
                
                disease_opts = ["高血压", "糖尿病", "两者均有", "无"]
                new_disease = st.selectbox("慢性病类型", disease_opts, 
                                           index=disease_opts.index(old.get("disease_type", "无")) if old.get("disease_type") in disease_opts else 0)
                
                if st.form_submit_button("保存修改"):
                    try:
                        bmi = round(new_weight / ((new_height/100) ** 2), 1) if new_height and new_weight else None
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE residents SET name=?, gender=?, age=?, phone=?, address=?, height=?, weight=?, bmi=?, smoking=?, drinking=?, emergency_contact=?, emergency_phone=?, disease_type=?
                            WHERE id_card=?
                        ''', (new_name, new_gender, new_age, new_phone, new_address, new_height, new_weight, bmi, new_smoking, new_drinking, new_emergency, new_emergency_phone, new_disease, search_id))
                        conn.commit()
                        st.success("修改成功！")
                        del st.session_state["edit_data"]
                    except Exception as e:
                        st.error(f"修改失败：{e}")
    
    # 删除档案
    with tab3:
        st.subheader("删除居民信息")
        st.warning("删除操作不可恢复，会同时删除该居民的所有医院记录和设备数据！")
        del_id = st.text_input("输入要删除的居民身份证号", key="del_id")
        confirm = st.checkbox("我确认要删除该居民及其所有相关数据")
        if st.button("删除居民", key="del_btn"):
            if del_id and confirm:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM hospital_records WHERE id_card = ?", (del_id,))
                    cursor.execute("DELETE FROM device_data WHERE id_card = ?", (del_id,))
                    cursor.execute("DELETE FROM residents WHERE id_card = ?", (del_id,))
                    conn.commit()
                    st.success("删除成功！")
                except Exception as e:
                    st.error(f"删除失败：{e}")
            elif not confirm:
                st.warning("请勾选确认框")
            else:
                st.warning("请输入身份证号")
    
    # 批量导入
    with tab4:
        st.subheader("批量导入居民档案")
        st.caption("支持 Excel (.xlsx) 或 CSV 文件，必须包含 name, id_card 列")
        
        uploaded_file = st.file_uploader("上传文件", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_import = pd.read_csv(uploaded_file, encoding="utf-8")
                else:
                    df_import = pd.read_excel(uploaded_file)
                
                if "name" not in df_import.columns or "id_card" not in df_import.columns:
                    st.error("文件必须包含 name 和 id_card 列")
                else:
                    for col in ["gender", "age", "phone", "address", "disease_type", "height", "weight", "smoking", "drinking", "emergency_contact", "emergency_phone"]:
                        if col not in df_import.columns:
                            if col == "height":
                                df_import[col] = 165
                            elif col == "weight":
                                df_import[col] = 65
                            else:
                                df_import[col] = None
                    
                    df_import["bmi"] = df_import.apply(
                        lambda r: round(r["weight"] / ((r["height"]/100)**2), 1) if r.get("height") and r.get("weight") else None, axis=1)
                    df_import = df_import.drop_duplicates(subset=["id_card"], keep="first")
                    
                    cursor = conn.cursor()
                    for _, row in df_import.iterrows():
                        try:
                            cursor.execute('''
                                INSERT INTO residents (name, id_card, gender, age, phone, address, disease_type, height, weight, bmi, smoking, drinking, emergency_contact, emergency_phone)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (row.get("name"), row.get("id_card"), row.get("gender"), row.get("age"), row.get("phone"), row.get("address"), row.get("disease_type"), row.get("height"), row.get("weight"), row.get("bmi"), row.get("smoking"), row.get("drinking"), row.get("emergency_contact"), row.get("emergency_phone")))
                        except:
                            pass
                    conn.commit()
                    st.success(f"导入成功！共 {len(df_import)} 条")
            except Exception as e:
                st.error(f"导入失败：{e}")

# ==================== 关联查询模块 ====================
elif menu == "关联查询":
    st.subheader("🔗 多源数据关联查询")
    
    st.markdown("### 1️⃣ 按身份证号精确查询")
    id_card = st.text_input("请输入居民身份证号", placeholder="18位身份证号码", key="exact_query")
    
    if st.button("查询完整健康档案", key="exact_btn"):
        if id_card:
            try:
                df_resident = read_sql(f"SELECT * FROM residents WHERE id_card = '{id_card}'")
                df_hospital = read_sql(f"SELECT * FROM hospital_records WHERE id_card = '{id_card}'")
                df_device = read_sql(f"SELECT * FROM device_data WHERE id_card = '{id_card}'")
                
                if not df_resident.empty:
                    st.subheader("👤 基本信息")
                    st.dataframe(df_resident)
                    
                    st.subheader("🏥 医院诊疗记录")
                    if not df_hospital.empty:
                        st.dataframe(df_hospital)
                    else:
                        st.info("暂无医院诊疗记录")
                    
                    st.subheader("📊 智能设备监测数据")
                    if not df_device.empty:
                        st.dataframe(df_device)
                    else:
                        st.info("暂无设备监测数据")
                else:
                    st.error("未找到该居民信息")
            except Exception as e:
                st.error(f"查询失败：{e}")
        else:
            st.warning("请输入身份证号")
    
    st.markdown("---")
    st.markdown("### 2️⃣ 按条件筛选居民")
    st.caption("可根据年龄、疾病类型、血压、血糖、吸烟饮酒等条件筛选")
    
    df_res = read_sql("SELECT * FROM residents")
    df_dev = read_sql("""
        SELECT d1.id_card, d1.systolic, d1.diastolic, d1.blood_sugar, d1.measure_date
        FROM device_data d1
        WHERE d1.measure_date = (SELECT MAX(measure_date) FROM device_data d2 WHERE d2.id_card = d1.id_card)
    """)
    
    df_merged = df_res.merge(df_dev, on='id_card', how='left')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        age_min = st.number_input("最小年龄", 0, 120, 0, key="age_min")
        age_max = st.number_input("最大年龄", 0, 120, 120, key="age_max")
    with col2:
        disease_filter = st.selectbox("慢性病类型", ["全部", "高血压", "糖尿病", "两者均有", "无"], key="disease_filter")
    with col3:
        bp_filter = st.selectbox("血压状态", ["全部", "血压偏高（高压≥140或低压≥90）", "血压正常（高压<140且低压<90）"], key="bp_filter")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        sugar_filter = st.selectbox("血糖状态", ["全部", "血糖偏高（≥7.0）", "血糖正常（<7.0）"], key="sugar_filter")
    with col5:
        smoke_filter = st.selectbox("吸烟状态", ["全部", "吸烟", "不吸烟"], key="smoke_filter")
    with col6:
        drink_filter = st.selectbox("饮酒状态", ["全部", "饮酒", "不饮酒"], key="drink_filter")
    
    if st.button("🔍 开始筛选", key="filter_btn"):
        df_result = df_merged.copy()
        df_result = df_result[(df_result['age'] >= age_min) & (df_result['age'] <= age_max)]
        if disease_filter != "全部":
            df_result = df_result[df_result['disease_type'] == disease_filter]
        if bp_filter == "血压偏高（高压≥140或低压≥90）":
            df_result = df_result[(df_result['systolic'] >= 140) | (df_result['diastolic'] >= 90)]
        elif bp_filter == "血压正常（高压<140且低压<90）":
            df_result = df_result[(df_result['systolic'] < 140) & (df_result['diastolic'] < 90)]
        if sugar_filter == "血糖偏高（≥7.0）":
            df_result = df_result[df_result['blood_sugar'] >= 7.0]
        elif sugar_filter == "血糖正常（<7.0）":
            df_result = df_result[df_result['blood_sugar'] < 7.0]
        if smoke_filter == "吸烟":
            df_result = df_result[df_result['smoking'] != "从不吸烟"]
        elif smoke_filter == "不吸烟":
            df_result = df_result[df_result['smoking'] == "从不吸烟"]
        if drink_filter == "饮酒":
            df_result = df_result[df_result['drinking'] != "从不饮酒"]
        elif drink_filter == "不饮酒":
            df_result = df_result[df_result['drinking'] == "从不饮酒"]
        
        if not df_result.empty:
            st.success(f"共找到 {len(df_result)} 位符合条件的居民")
            display_cols = ['name', 'id_card', 'age', 'gender', 'disease_type', 'systolic', 'diastolic', 'blood_sugar', 'smoking', 'drinking']
            st.dataframe(df_result[display_cols], use_container_width=True)
            
            st.subheader("📋 查看居民详细档案")
            selected_name = st.selectbox("选择居民查看完整档案", df_result['name'].tolist(), key="select_resident")
            if selected_name:
                selected_id = df_result[df_result['name'] == selected_name]['id_card'].iloc[0]
                df_detail_res = read_sql(f"SELECT * FROM residents WHERE id_card = '{selected_id}'")
                df_detail_hos = read_sql(f"SELECT * FROM hospital_records WHERE id_card = '{selected_id}'")
                df_detail_dev = read_sql(f"SELECT * FROM device_data WHERE id_card = '{selected_id}' ORDER BY measure_date DESC LIMIT 10")
                
                st.subheader("👤 基本信息")
                st.dataframe(df_detail_res)
                st.subheader("🏥 医院诊疗记录")
                if not df_detail_hos.empty:
                    st.dataframe(df_detail_hos)
                else:
                    st.info("暂无医院诊疗记录")
                st.subheader("📊 最近设备监测数据")
                if not df_detail_dev.empty:
                    st.dataframe(df_detail_dev)
                else:
                    st.info("暂无设备监测数据")
        else:
            st.warning("未找到符合条件的居民")

# ==================== 预警提示模块 ====================
elif menu == "预警提示":
    st.subheader("⚠️ 健康预警提示")
    st.caption("📌 单次异常：最新一次测量值超标 | 🔴 连续异常：最近连续3次及以上超标（突出提示）")
    
    try:
        df_res = read_sql("SELECT id_card, name, phone, disease_type FROM residents")
        df_dev = read_sql("SELECT id_card, systolic, diastolic, blood_sugar, measure_date FROM device_data ORDER BY id_card, measure_date DESC")
        
        if df_dev.empty:
            st.warning("暂无设备监测数据")
            st.stop()
        
        df_latest = df_dev.drop_duplicates(subset=['id_card'], keep='first')
        df_latest = df_latest.merge(df_res, on='id_card', how='inner')
        
        df_latest['单次血压预警'] = df_latest.apply(
            lambda x: '⚠️ 血压偏高' if (x['systolic'] >= 140 or x['diastolic'] >= 90) else '', axis=1)
        df_latest['单次血糖预警'] = df_latest.apply(
            lambda x: '⚠️ 血糖偏高' if x['blood_sugar'] >= 7.0 else '', axis=1)
        
        def check_consecutive(df_person):
            if df_person.empty or len(df_person) < 3:
                return False, False, 0, 0
            df_person = df_person.sort_values('measure_date')
            df_person['血压异常'] = (df_person['systolic'] >= 140) | (df_person['diastolic'] >= 90)
            df_person['血糖异常'] = df_person['blood_sugar'] >= 7.0
            
            max_bp, cur_bp = 0, 0
            for flag in df_person['血压异常']:
                if flag:
                    cur_bp += 1
                    max_bp = max(max_bp, cur_bp)
                else:
                    cur_bp = 0
            
            max_bs, cur_bs = 0, 0
            for flag in df_person['血糖异常']:
                if flag:
                    cur_bs += 1
                    max_bs = max(max_bs, cur_bs)
                else:
                    cur_bs = 0
            
            return max_bp >= 3, max_bs >= 3, max_bp, max_bs
        
        continuous_alerts = []
        for id_card in df_latest['id_card'].unique():
            person_data = df_dev[df_dev['id_card'] == id_card]
            bp_cont, bs_cont, bp_days, bs_days = check_consecutive(person_data)
            continuous_alerts.append({
                'id_card': id_card,
                'bp_consecutive': bp_cont,
                'bs_consecutive': bs_cont,
                'bp_days': bp_days,
                'bs_days': bs_days
            })
        
        df_continuous = pd.DataFrame(continuous_alerts)
        df_alert = df_latest.merge(df_continuous, on='id_card', how='left')
        
        def make_continuous_text(row):
            texts = []
            if row['bp_consecutive']:
                texts.append(f'🔴 连续{row["bp_days"]}次血压偏高')
            if row['bs_consecutive']:
                texts.append(f'🔴 连续{row["bs_days"]}次血糖偏高')
            return ' | '.join(texts) if texts else ''
        
        df_alert['连续预警'] = df_alert.apply(make_continuous_text, axis=1)
        alert_df = df_alert[(df_alert['单次血压预警'] != '') | (df_alert['单次血糖预警'] != '') | (df_alert['连续预警'] != '')]
        
        if not alert_df.empty:
            st.warning("🔔 连续异常预警说明：连续3次及以上测量指标超标，请重点关注！")
            display_cols = ['name', 'id_card', 'systolic', 'diastolic', 'blood_sugar', 'measure_date', '单次血压预警', '单次血糖预警', '连续预警']
            st.dataframe(alert_df[display_cols], use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("单次血压偏高人数", alert_df[alert_df['单次血压预警'] != ''].shape[0])
            col2.metric("单次血糖偏高人数", alert_df[alert_df['单次血糖预警'] != ''].shape[0])
            col3.metric("连续异常人数（需重点关注）", alert_df[alert_df['连续预警'] != ''].shape[0])
            
            st.subheader("📋 查看异常居民详细档案")
            alert_df['display_name'] = alert_df['name'] + "（" + alert_df['id_card'] + "）"
            selected_display = st.selectbox("选择居民查看详情", alert_df['display_name'].tolist(), key="alert_select")
            if selected_display:
                selected_id = alert_df[alert_df['display_name'] == selected_display]['id_card'].iloc[0]
                df_detail_res = read_sql(f"SELECT * FROM residents WHERE id_card = '{selected_id}'")
                df_detail_hos = read_sql(f"SELECT * FROM hospital_records WHERE id_card = '{selected_id}'")
                df_detail_dev = read_sql(f"SELECT * FROM device_data WHERE id_card = '{selected_id}' ORDER BY measure_date DESC LIMIT 10")
                
                st.subheader("👤 基本信息")
                st.dataframe(df_detail_res)
                st.subheader("🏥 医院诊疗记录")
                if not df_detail_hos.empty:
                    st.dataframe(df_detail_hos)
                else:
                    st.info("暂无医院诊疗记录")
                st.subheader("📊 最近设备监测数据")
                if not df_detail_dev.empty:
                    st.dataframe(df_detail_dev)
                else:
                    st.info("暂无设备监测数据")
        else:
            st.success("暂无异常预警记录，所有居民健康状况良好")
    except Exception as e:
        st.error(f"预警模块加载失败：{e}")

# ==================== 可视化模块 ====================
else:
    st.subheader("📈 数据可视化分析")
    
    df_res = read_sql("SELECT * FROM residents")
    df_dev = read_sql("SELECT * FROM device_data")
    
    st.subheader("📊 慢性病类型分布")
    disease_counts = df_res['disease_type'].value_counts()
    if not disease_counts.empty:
        st.plotly_chart(px.pie(disease_counts, names=disease_counts.index, values=disease_counts.values, title='慢性病类型分布'), use_container_width=True)
    else:
        st.info("暂无慢性病数据")
    
    st.subheader("🏘️ 各社区慢病人数统计")
    community_disease = df_res.groupby(['address', 'disease_type']).size().unstack(fill_value=0)
    if not community_disease.empty:
        st.plotly_chart(px.bar(community_disease, title='各社区疾病类型分布'), use_container_width=True)
    else:
        st.info("暂无社区数据")
    
    st.subheader("🚬 生活方式统计")
    col1, col2 = st.columns(2)
    with col1:
        smoking_counts = df_res['smoking'].value_counts()
        if not smoking_counts.empty:
            st.write("**吸烟情况**")
            st.plotly_chart(px.bar(smoking_counts, title='吸烟统计'), use_container_width=True)
    with col2:
        drinking_counts = df_res['drinking'].value_counts()
        if not drinking_counts.empty:
            st.write("**饮酒情况**")
            st.plotly_chart(px.bar(drinking_counts, title='饮酒统计'), use_container_width=True)
    
    st.subheader("📏 身高与体重关系")
    if 'height' in df_res.columns and 'weight' in df_res.columns:
        st.plotly_chart(px.scatter(df_res, x='height', y='weight', color='disease_type', title='身高-体重分布'), use_container_width=True)
    
    st.subheader("❤️ 心率分布情况")
    if not df_dev.empty and 'heart_rate' in df_dev.columns:
        st.plotly_chart(px.histogram(df_dev, x='heart_rate', nbins=20, title='心率分布'), use_container_width=True)
    else:
        st.info("暂无心率数据")
    
    st.subheader("⚠️ 预警统计")
    if not df_dev.empty:
        df_dev['血压预警'] = df_dev.apply(lambda x: (x['systolic'] >= 140 or x['diastolic'] >= 90), axis=1)
        df_dev['血糖预警'] = df_dev.apply(lambda x: x['blood_sugar'] >= 7.0, axis=1)
        alert_count = df_dev.groupby('id_card').agg({'血压预警': 'max', '血糖预警': 'max'}).reset_index()
        alert_summary = {
            '血压偏高人数': alert_count[alert_count['血压预警']].shape[0],
            '血糖偏高人数': alert_count[alert_count['血糖预警']].shape[0],
            '两者均偏高': alert_count[alert_count['血压预警'] & alert_count['血糖预警']].shape[0]
        }
        col1, col2, col3 = st.columns(3)
        col1.metric("血压偏高人数", alert_summary['血压偏高人数'])
        col2.metric("血糖偏高人数", alert_summary['血糖偏高人数'])
        col3.metric("两者均偏高", alert_summary['两者均偏高'])
    
    st.subheader("📉 居民血压变化趋势")
    id_card = st.text_input("输入身份证号查看血压趋势", key="viz_id")
    if id_card:
        df_bp = read_sql(f"SELECT measure_date, systolic, diastolic FROM device_data WHERE id_card = '{id_card}' ORDER BY measure_date")
        if not df_bp.empty:
            st.plotly_chart(px.line(df_bp, x='measure_date', y=['systolic', 'diastolic'], title='血压趋势'), use_container_width=True)
        else:
            st.info("暂无该居民血压数据")