import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(
    page_title="Environmental Health Surveillance Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

DISEASE_DICT = {
    'J62.8': {'name': 'โรคปอดจากฝุ่นหิน/ฝุ่นปูน (Pneumoconiosis)', 'cat': 'กลุ่มโรคทางเดินหายใจและปอด (ผลกระทบโรงปูน/ฝุ่น)'},
    'J44': {'name': 'โรคปอดอุดกั้นเรื้อรัง (COPD)', 'cat': 'กลุ่มโรคทางเดินหายใจและปอด (ผลกระทบโรงปูน/ฝุ่น)'},
    'J45': {'name': 'โรคหอบหืด (Asthma)', 'cat': 'กลุ่มโรคทางเดินหายใจและปอด (ผลกระทบโรงปูน/ฝุ่น)'},
    'J30': {'name': 'โรคจมูกอักเสบภูมิแพ้ / แพ้อากาศ', 'cat': 'กลุ่มโรคทางเดินหายใจและปอด (ผลกระทบโรงปูน/ฝุ่น)'},
    'J00-J06': {'name': 'โรคติดเชื้อระบบทางเดินหายใจส่วนบนเฉียบพลัน', 'cat': 'กลุ่มโรคทางเดินหายใจและปอด (ผลกระทบโรงปูน/ฝุ่น)'},
    'L24': {'name': 'ผิวหนังอักเสบจากการระคายเคือง (แพ้ปูน/สารเคมี)', 'cat': 'กลุ่มโรคผิวหนังและดวงตา (ผลกระทบฝุ่นปูน/สารเคมี)'},
    'H10': {'name': 'เยื่อบุตาอักเสบ (ตาแดงจากฝุ่นระคายเคือง)', 'cat': 'กลุ่มโรคผิวหนังและดวงตา (ผลกระทบฝุ่นปูน/สารเคมี)'},
    'A09': {'name': 'โรคอุจจาระร่วงและกระเพาะลำไส้อักเสบจากการติดเชื้อ', 'cat': 'กลุ่มโรคที่เกี่ยวข้องกับน้ำเสียและการสุขาภิบาล'},
    'A00-A08': {'name': 'โรคติดเชื้อทางเดินอาหารอื่น ๆ (บิด/ไทฟอยด์/อาหารเป็นพิษ)', 'cat': 'กลุ่มโรคที่เกี่ยวข้องกับน้ำเสียและการสุขาภิบาล'},
    'A27': {'name': 'โรคฉี่หนู (Leptospirosis)', 'cat': 'กลุ่มโรคที่เกี่ยวข้องกับน้ำเสียและการสุขาภิบาล'},
    'B15': {'name': 'ไวรัสตับอักเสบ เอ', 'cat': 'กลุ่มโรคที่เกี่ยวข้องกับน้ำเสียและการสุขาภิบาล'}
}

def map_main_disease_code(code):
    c = str(code).strip().upper().replace('.', '')
    if c.startswith('J628'): return 'J62.8'
    if c.startswith('J44'): return 'J44'
    if c.startswith('J45'): return 'J45'
    if c.startswith('J30'): return 'J30' 
    if c.startswith(('J00','J01','J02','J03','J04','J05','J06')): return 'J00-J06'
    if c.startswith('L24'): return 'L24'
    if c.startswith('H10'): return 'H10'
    if c.startswith('A09'): return 'A09'
    if c.startswith(('A00','A01','A02','A03','A04','A05','A06','A07','A08')): return 'A00-A08' 
    if c.startswith('A27'): return 'A27'
    if c.startswith('B15'): return 'B15'
    return 'Other'

data_file = "dashboard_data.xlsx"

@st.cache_data
def load_aggregated_data():
    if not os.path.exists(data_file):
        return None, None, None
    
    df_m = pd.read_excel(data_file, sheet_name='monthly')
    df_a = pd.read_excel(data_file, sheet_name='age')
    df_s = pd.read_excel(data_file, sheet_name='sex')
    
    for df in [df_m, df_a, df_s]:
        df['DIAGCODE'] = df['DIAGCODE'].apply(map_main_disease_code)
        df.drop(df[df['DIAGCODE'] == 'Other'].index, inplace=True)
        df['DIAG_NAME'] = df['DIAGCODE'].apply(lambda x: DISEASE_DICT[x]['name'])
        df['DIAG_CAT'] = df['DIAGCODE'].apply(lambda x: DISEASE_DICT[x]['cat'])
        
    df_m = df_m.groupby(['Group', 'DIAG_CAT', 'DIAGCODE', 'DIAG_NAME', 'YEAR_MONTH', 'FAMP'], as_index=False)['PATIENT_COUNT'].sum()
    df_a = df_a.groupby(['Group', 'DIAG_CAT', 'DIAGCODE', 'DIAG_NAME', 'YEAR', 'FAMP', 'AGE_GROUP'], as_index=False)['PATIENT_COUNT'].sum()
    df_s = df_s.groupby(['Group', 'DIAG_CAT', 'DIAGCODE', 'DIAG_NAME', 'YEAR', 'FAMP', 'SEX_NAME'], as_index=False)['PATIENT_COUNT'].sum()

    return df_m, df_a, df_s

df_monthly, df_age, df_sex = load_aggregated_data()

st.title("🩺 ระบบเฝ้าระวังระบาดวิทยาและผลกระทบสิ่งแวดล้อมทางสุขภาพ")
st.caption("ศูนย์สารสนเทศระบาดวิทยา • วิเคราะห์แนวโน้มผลกระทบจากมลพิษทางอากาศ (โรงปูน/ฝุ่น) และการสุขาภิบาลน้ำเสีย")

if df_monthly is None or df_age is None or df_sex is None:
    st.error(f"❌ ไม่พบไฟล์ข้อมูลอนุกรม '{data_file}'")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("🔍 ตัวกรองข้อมูลแบบลำดับชั้น")
    
    all_groups = sorted(df_monthly['Group'].unique().tolist())
    selected_group_option = st.sidebar.selectbox("1. ระดับความรุนแรง (Group)", options=["ดูทั้งหมด (All)"] + all_groups, index=0)
    filter_group = all_groups if selected_group_option == "ดูทั้งหมด (All)" else [selected_group_option]
    
    mask_group = df_monthly['Group'].isin(filter_group)
    available_cats = sorted(df_monthly.loc[mask_group, 'DIAG_CAT'].unique().tolist())
    
    selected_cat_option = st.sidebar.selectbox("2. หมวดหมู่โรค (Category)", options=["ดูทั้งหมด (All Categories)"] + available_cats, index=0)
    filter_cat = available_cats if selected_cat_option == "ดูทั้งหมด (All Categories)" else [selected_cat_option]
    
    mask_cat = mask_group & df_monthly['DIAG_CAT'].isin(filter_cat)
    available_codes = sorted(df_monthly.loc[mask_cat, 'DIAGCODE'].unique().tolist())
    
    # 💡 ปรับแต่งเพื่อลดการใช้ Memory ตอนโหลดเว็บครั้งแรก
    # ตั้งค่าให้ตอนเปิดเว็บมา ไม่ได้เลือกทุกโรคทันที เพื่อให้ตารางกราฟเบาที่สุด
    select_all_codes = st.sidebar.checkbox("✅ ดูทุกรหัสโรค", value=False) 
    
    if select_all_codes:
        filter_codes = available_codes
        st.sidebar.info("คุณกำลังเลือกตรวจสอบทุกรหัสโรค")
    else:
        # ถ้าไม่ได้เลือกทั้งหมด ให้เลือกโรคแรกเป็นค่าเริ่มต้น
        default_code = [available_codes[0]] if available_codes else []
        filter_codes = st.sidebar.multiselect(
            "3. เจาะลึกรหัสโรค (DIAGCODE)", 
            options=available_codes,
            default=default_code, 
            format_func=lambda x: f"{x} : {DISEASE_DICT.get(x, {'name': 'ไม่ระบุ'})['name']}",
            key="ms_code"
        )
        if not filter_codes:
            st.sidebar.warning("⚠️ กรุณาเลือกรหัสโรค")

    mask_code = mask_cat & df_monthly['DIAGCODE'].isin(filter_codes)
    available_amps = sorted(df_monthly.loc[mask_code, 'FAMP'].dropna().unique().tolist())
    
    select_all_amps = st.sidebar.checkbox("✅ เลือกทุกพื้นที่ศึกษา", value=True)
    if select_all_amps:
        filter_amps = available_amps
        st.sidebar.info("คุณกำลังเลือกดูทุกอำเภอ")
    else:
        filter_amps = st.sidebar.multiselect(
            "4. พื้นที่เฝ้าระวัง (อำเภอ/FAMP)", 
            options=available_amps,
            key="ms_amp"
        )
        if not filter_amps:
            st.sidebar.warning("⚠️ กรุณาเลือกพื้นที่")

    # --- Data Filtering ---
    if not filter_codes or not filter_amps:
        m_filtered = pd.DataFrame(columns=df_monthly.columns)
        a_filtered = pd.DataFrame(columns=df_age.columns)
        s_filtered = pd.DataFrame(columns=df_sex.columns)
    else:
        m_filtered = df_monthly[
            df_monthly['Group'].isin(filter_group) &
            df_monthly['DIAG_CAT'].isin(filter_cat) & 
            df_monthly['DIAGCODE'].isin(filter_codes) & 
            df_monthly['FAMP'].isin(filter_amps)
        ]
        a_filtered = df_age[
            df_age['Group'].isin(filter_group) &
            df_age['DIAG_CAT'].isin(filter_cat) & 
            df_age['DIAGCODE'].isin(filter_codes) & 
            df_age['FAMP'].isin(filter_amps)
        ]
        s_filtered = df_sex[
            df_sex['Group'].isin(filter_group) &
            df_sex['DIAG_CAT'].isin(filter_cat) & 
            df_sex['DIAGCODE'].isin(filter_codes) & 
            df_sex['FAMP'].isin(filter_amps)
        ]

    # --- UI Rendering ---
    if m_filtered.empty:
        st.warning("📭 ไม่พบข้อมูลสถิติที่ตรงกับเงื่อนไข หรือคุณอาจยังเลือกตัวกรองไม่ครบ กรุณาปรับเปลี่ยนตัวกรองทางแถบด้านซ้าย")
    else:
        total_cases = m_filtered['PATIENT_COUNT'].sum()
        acute_cases = m_filtered[m_filtered['Group'] == 'Acute']['PATIENT_COUNT'].sum()
        chronic_cases = m_filtered[m_filtered['Group'] == 'Chronic']['PATIENT_COUNT'].sum()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(label="จำนวนเคสผู้ป่วยรวมสะสม (ครั้ง)", value=f"{total_cases:,}")
        col_m2.metric(label="เคสเฉียบพลัน (Acute Exposure Trend)", value=f"{acute_cases:,}")
        col_m3.metric(label="เคสเรื้อรังสะสม (Chronic Dust Burden)", value=f"{chronic_cases:,}")
    
        tab_main, tab_time, tab_person, tab_meta = st.tabs([
            "🏥 1. ข้อมูลภาพรวมและพื้นที่", 
            "📈 2. อนุกรมเวลา (Time Series)", 
            "👥 3. ข้อมูลประชากร (Person)", 
            "📖 4. กรรมวิธีข้อมูล (Metadata)"
        ])
        
        with tab_main:
            st.subheader("📊 ตารางรวมสถิติตามพื้นที่และกลุ่มโรคย่อย")
            pivot_display = m_filtered.groupby(['DIAG_CAT', 'DIAGCODE', 'DIAG_NAME', 'FAMP', 'Group'], as_index=False)['PATIENT_COUNT'].sum()
            pivot_display.columns = ['กลุ่มอาการหลัก', 'รหัสโรค', 'ชื่อโรคทางการแพทย์', 'อำเภอ (FAMP)', 'ประเภทโรค', 'จำนวนผู้เจ็บป่วย (ครั้ง)']
            pivot_sorted = pivot_display.sort_values(by='จำนวนผู้เจ็บป่วย (ครั้ง)', ascending=False)
            
            # ใช้พารามิเตอร์ width แทน use_container_width (แก้แจ้งเตือนเวอร์ชันเก่า)
            st.dataframe(pivot_sorted, width=1200)
            
            if not pivot_display.empty:
                fig_area = px.bar(
                    pivot_sorted, 
                    x="อำเภอ (FAMP)", 
                    y="จำนวนผู้เจ็บป่วย (ครั้ง)", 
                    color="กลุ่มอาการหลัก",
                    barmode="group",
                    title="จำนวนเคสสะสมจำแนกตามพื้นที่ศึกษา"
                )
                st.plotly_chart(fig_area, use_container_width=True)

        with tab_time:
            st.subheader("📈 เส้นแนวโน้มอนุกรมเวลา (Epidemiological Time Series)")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                split_disease = st.radio("🦠 รูปแบบการแสดงผล (ตามโรค):", ["รวมทุกโรคเป็นเส้นเดียว (Total)", "แยกเส้นตามรหัสโรค (By Disease)"], index=1)
            with col_t2:
                split_area = st.radio("📍 รูปแบบการแสดงผล (ตามพื้นที่):", ["รวมทุกอำเภอเป็นเส้นเดียว (Total)", "แยกเส้นตามอำเภอ (By Area)"], index=0)
            
            if not m_filtered.empty:
                groupby_cols = ['YEAR_MONTH']
                hover_data = []
                
                if split_disease == "แยกเส้นตามรหัสโรค (By Disease)":
                    groupby_cols.extend(['DIAGCODE', 'DIAG_NAME'])
                    hover_data.append('DIAG_NAME')
                if split_area == "แยกเส้นตามอำเภอ (By Area)":
                    groupby_cols.append('FAMP')
                    
                try:
                    time_series = m_filtered.groupby(groupby_cols, as_index=False)['PATIENT_COUNT'].sum()
                    time_series = time_series.sort_values(by='YEAR_MONTH')
                    
                    if split_disease == "แยกเส้นตามรหัสโรค (By Disease)" and split_area == "แยกเส้นตามอำเภอ (By Area)":
                        time_series['Legend'] = time_series['DIAGCODE'] + " (" + time_series['FAMP'] + ")"
                        color_col = 'Legend'
                    elif split_disease == "แยกเส้นตามรหัสโรค (By Disease)":
                        color_col = 'DIAGCODE'
                    elif split_area == "แยกเส้นตามอำเภอ (By Area)":
                        color_col = 'FAMP'
                    else:
                        color_col = None

                    has_enough_data = len(time_series['YEAR_MONTH'].unique()) >= 2
                    
                    if has_enough_data:
                        fig_time = px.line(
                            time_series, x='YEAR_MONTH', y='PATIENT_COUNT', color=color_col,
                            hover_data=hover_data if hover_data else None,
                            labels={'YEAR_MONTH': 'ปี-เดือน', 'PATIENT_COUNT': 'จำนวนผู้ป่วย', color_col: 'คำอธิบาย'},
                            markers=True
                        )
                        fig_time.update_layout(hovermode="x unified")
                    else:
                        st.info("💡 ข้อมูลมีจำนวนเดือนน้อยเกินไปที่จะลากเส้นต่อเนื่องได้ ระบบจึงแสดงผลเป็นจุดแทน")
                        fig_time = px.scatter(
                            time_series, x='YEAR_MONTH', y='PATIENT_COUNT', color=color_col,
                            hover_data=hover_data if hover_data else None,
                            labels={'YEAR_MONTH': 'ปี-เดือน', 'PATIENT_COUNT': 'จำนวนผู้ป่วย', color_col: 'คำอธิบาย'}
                        )
                        fig_time.update_traces(marker=dict(size=12))

                    st.plotly_chart(fig_time, use_container_width=True)
                except Exception:
                    st.warning("⚠️ รูปแบบการกรองซับซ้อนเกินไป ลองปรับลดการแยกเส้นดูครับ")

        with tab_person:
            st.subheader("👥 การกระจายตัวตามคุณลักษณะบุคคล (Demographic Distribution)")
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.write("#### 👶👵 โครงสร้างจำแนกตามกลุ่มอายุ")
                if not a_filtered.empty:
                    age_summary = a_filtered.groupby(['AGE_GROUP'], as_index=False)['PATIENT_COUNT'].sum()
                    age_order = {'0-5 ปี': 0, '6-15 ปี': 1, '16-35 ปี': 2, '36-60 ปี': 3, 'มากกว่า 60 ปี': 4, 'ไม่ระบุ': 5}
                    age_summary['order'] = age_summary['AGE_GROUP'].map(age_order)
                    age_summary = age_summary.sort_values(by='order')
                    
                    st.dataframe(age_summary[['AGE_GROUP', 'PATIENT_COUNT']], width=400)
                    fig_age = px.bar(age_summary, x='AGE_GROUP', y='PATIENT_COUNT', color='AGE_GROUP')
                    st.plotly_chart(fig_age, use_container_width=True)
                    
            with col_p2:
                st.write("#### 🚻 อัตราส่วนสัดส่วนทางเพศ")
                if not s_filtered.empty:
                    sex_summary = s_filtered.groupby(['SEX_NAME'], as_index=False)['PATIENT_COUNT'].sum()
                    st.dataframe(sex_summary, width=400)
                    fig_sex = px.pie(
                        sex_summary, values='PATIENT_COUNT', names='SEX_NAME', color='SEX_NAME',
                        color_discrete_map={'ชาย': '#2b5c8f', 'หญิง': '#e86184', 'ไม่ระบุ': '#9fa3a6'}
                    )
                    st.plotly_chart(fig_sex, use_container_width=True)
    
        with tab_meta:
            st.subheader("📋 คำอธิบายพจนานุกรมรหัสโรคเฝ้าระวังหลักทางระบาดวิทยา")
            st.markdown("""
            * **J62.8 (Pneumoconiosis):** โรคปอดจากฝุ่นหิน/ฝุ่นปูน (ดัชนีชี้วัดตรงประเด็นกับมลพิษอุตสาหกรรมโรงปูนซีเมนต์และการโม่หินที่สุด)
            * **J44 (COPD):** โรคปอดอุดกั้นเรื้อรัง บ่งชี้ผลกระทบระยะยาวของระบบทางเดินหายใจเมื่อสัมผัสสารระคายเคือง
            * **J45 (Asthma):** โรคหอบหืด (มักเกิดภาวะกำเริบเฉียบพลัน [Acute Exacerbation] เมื่อปริมาณฝุ่นละอองขนาดเล็กหนาแน่น)
            * **J30 (Allergic rhinitis):** โรคจมูกอักเสบภูมิแพ้ / แพ้อากาศ ชี้วัดปฏิกิริยาเยื่อบุทางเดินหายใจส่วนบน
            * **J00 - J06 (Acute upper respiratory infections):** โรคติดเชื้อระบบทางเดินหายใจส่วนบนเฉียบพลัน
            * **L24 (Irritant contact dermatitis):** ผิวหนังอักเสบจากการระคายเคือง ประเมินผลกระทบจากฝุ่นปูนซีเมนต์ที่มีความเป็นด่าง
            * **H10 (Conjunctivitis):** เยื่อบุตาอักเสบ หรืออาการตาแดงจากการระคายเคืองทางกายภาพของฝุ่น
            * **A09 (Diarrhoea):** โรคอุจจาระร่วงและกระเพาะลำไส้อักเสบจากการติดเชื้อ
            * **A00 - A08:** โรคติดเชื้อทางเดินอาหารอื่น ๆ เช่น บิด, ไทฟอยด์, อาหารเป็นพิษ
            * **A27 (Leptospirosis):** โรคฉี่หนู มักพบบันทึกสถิติสูงขึ้นอย่างมีนัยสำคัญในพื้นที่น้ำเสียขัง
            * **B15 (Acute hepatitis A):** ไวรัสตับอักเสบ เอ
            """)
            st.markdown("---")
            st.subheader("⚙️ ขั้นตอนกระบวนการวิเคราะห์ข้อมูล")
            st.info("""
            1. **แหล่งข้อมูล:** HDC กระทรวงสาธารณสุข
            2. **Data Cleaning:** ระบุพื้นที่ผู้ป่วยที่ชัดเจน คำนวณอายุ
            3. **De-duplication:** โรค Chronic (J62.8) คัดกรองเคสซ้ำรายคนออก
            4. **Data Aggregation:** ข้อมูลถูกสรุปรวม (Count) และลบฟิลด์ระบุตัวตนออก 100% ทำให้ปลอดภัยตามหลัก PDPA
            """)
    
        st.sidebar.markdown("---")
        st.sidebar.subheader("📥 ดาวน์โหลดชุดข้อมูลสถิติระบาดวิทยา")
        csv_data = m_filtered[['Group', 'DIAGCODE', 'DIAG_NAME', 'YEAR_MONTH', 'FAMP', 'PATIENT_COUNT']].to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(label="ดาวน์โหลดข้อมูลตามฟิลเตอร์ (.csv)", data=csv_data, file_name="epidemiological_data.csv", mime="text/csv")