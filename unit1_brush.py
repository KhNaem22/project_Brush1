import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials



permanent_fixed_upper = {}
permanent_fixed_lower = {}
permanent_yellow_upper = {}
permanent_yellow_lower = {}

permanent_lock_upper = set()
permanent_lock_lower = set()

permanent_fixed_upper = st.session_state.get("permanent_fixed_upper", {})
permanent_yellow_upper = st.session_state.get("permanent_yellow_upper", {})

st.set_page_config(page_title="Brush Dashboard", layout="wide")

page = st.sidebar.radio("📂 เลือกหน้า", [
    "📊 หน้าแสดงผล rate และ ชั่วโมงที่เหลือ",
    "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม",
    "📈 พล็อตกราฟตามเวลา (แยก Upper และ Lower)"])


def load_config_from_sheet(sh, sheet_name):
    ws = sh.worksheet(sheet_name)
    try:
        sheet_count = int(ws.acell("B41").value)
        min_required = int(ws.acell("B42").value)
        threshold_percent = float(ws.acell("B43").value)
        alert_threshold_hours = int(ws.acell("B44").value)
        length_threshold = float(ws.acell("B45").value)
        return sheet_count, min_required, threshold_percent, alert_threshold_hours, length_threshold
    except:
        return 7, 5, 5.0, 50, 35.0



def save_config_to_sheet(sh, sheet_name, sheet_count, min_required, threshold_percent, alert_threshold_hours,length_threshold):
    try:
        ws = sh.worksheet(sheet_name)
        ws.update("B41", [[sheet_count]])
        ws.update("B42", [[min_required]])
        ws.update("B43", [[threshold_percent]])
        ws.update("B44", [[alert_threshold_hours]])
        ws.update("B45", [[length_threshold]])

    except Exception as e:
        st.error(f"❌ ไม่สามารถบันทึก config ลงชีตได้: {e}")
        
@st.cache_resource(ttl=300)
def get_google_sheet():
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    return gc.open_by_url("https://docs.google.com/spreadsheets/d/1ZLpTZAqqGYQgoqvlCSg9ku4SXUtH7Fas4Z8egT4HNXY/edit?usp=sharing")

# ✅ ใช้ทุกหน้าแทน gc.open_by_url()
sh = get_google_sheet()

@st.cache_data(ttl=300)
def load_excel_bytes(sheet_url):
    response = requests.get(sheet_url)
    return response.content

@st.cache_data(ttl=300)
def get_sheet_names_cached():
    return [ws.title for ws in get_google_sheet().worksheets()]


# ด้านบนสุดของไฟล์

import requests
from io import BytesIO

sheet_id = "1ZLpTZAqqGYQgoqvlCSg9ku4SXUtH7Fas4Z8egT4HNXY"
sheet_url_export = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"


xls_bytes = load_excel_bytes(sheet_url_export)
xls = pd.ExcelFile(BytesIO(xls_bytes), engine="openpyxl")


ws_sheet1 = sh.worksheet("Sheet1")  # ✅ เรียกครั้งเดียว


# --------------------------------------------------- PAGE 2 -------------------------------------------------


if page == "📝 กรอกข้อมูลแปลงถ่านเพิ่มเติม":
    st.title("📝 กรอกข้อมูลแปรงถ่าน + ชั่วโมง")
    
  






    sh = get_google_sheet()

# ✅ ดึงเฉพาะชีตที่ชื่อขึ้นต้นด้วย Sheet (หรือเปลี่ยนเป็นตาม pattern ของคุณ เช่น "Sheet1", "Sheet2", ...)
    # ✅ 1. เตรียมรายชื่อชีตทั้งหมดแบบ normalize (รองรับ sheet ชื่อเล็ก/ใหญ่)


    sheet_names_all = [ws.title for ws in sh.worksheets()]

    def extract_sheet_number(name):
        try:
            return int(name.lower().replace("sheet", ""))
        except:
            return float("inf")

    sheet_names = [s for s in sheet_names_all if s.lower().startswith("sheet")]
    sheet_names_sorted = sorted(sheet_names, key=extract_sheet_number)
    if "Sheet1" in sheet_names_sorted:
        sheet_names_sorted.remove("Sheet1")
        sheet_names_sorted = ["Sheet1"] + sheet_names_sorted

    sheet_names = sheet_names_sorted

    filtered_sheet_names = [s for s in sheet_names_all if s.lower().startswith("sheet") and s.lower() != "sheet1"]

    # ✅ 2. ดึงตัวเลขของ SheetN
    sheet_numbers = []
    for name in filtered_sheet_names:
        suffix = name.lower().replace("sheet", "")
        if suffix.isdigit():
            sheet_numbers.append(int(suffix))

    sheet_numbers.sort()
    next_sheet_number = sheet_numbers[-1] + 1 if sheet_numbers else 2
    next_sheet_name = f"Sheet{next_sheet_number}"

    # ทำให้ sheet มีการเรียงกัน
    def extract_sheet_number(name):
        try:
            return int(name.lower().replace("sheet", ""))
        except:
            return float('inf')  # สำหรับกรณีชื่อไม่ใช่ตัวเลข

    sheet_names = [s for s in sheet_names_all if s.lower().startswith("sheet")]
    sheet_names_sorted = sorted(sheet_names, key=extract_sheet_number)

    # ถ้าอยากให้ Sheet1 อยู่บนสุดเสมอ:
    if "Sheet1" in sheet_names_sorted:
        sheet_names_sorted.remove("Sheet1")
        sheet_names_sorted = ["Sheet1"] + sheet_names_sorted

    sheet_names = sheet_names_sorted
    
    
    filtered_sheet_names = [s for s in sheet_names if s.lower() != "sheet1"]
    sheet_numbers = [
        int(s.lower().replace("sheet", "")) 
        for s in filtered_sheet_names if s.lower().replace("sheet", "").isdigit()
    ]
    sheet_numbers.sort()

    next_sheet_number = sheet_numbers[-1] + 1 if sheet_numbers else 2
    next_sheet_name = f"Sheet{next_sheet_number}"
    
    selected_sheet_auto = st.session_state.get("selected_sheet_auto", "Sheet1")
    if selected_sheet_auto not in sheet_names:
        selected_sheet_auto = sheet_names[0]  # fallback เผื่อ sheet ใหม่ยังไม่เจอทัน

    selected_sheet = st.selectbox("📄 เลือก Sheet ที่ต้องการกรอกข้อมูล", sheet_names_sorted)

    #st.write(f"🧪 Selected (auto): {selected_sheet_auto}")
    #st.write(f"🧪 Dropdown Options: {sheet_names}")
   

        # ✅ เตรียมชื่อชีตถัดไป (เช่น Sheet13)
    
    
    next_sheet_number = sheet_numbers[-1] + 1 if sheet_numbers else 2
    next_sheet_name = f"Sheet{next_sheet_number}"

    


        # ดึงเลขชีตล่าสุดก่อนแสดงปุ่ม
    filtered_sheet_names = [s for s in sheet_names if s.lower().startswith("sheet") and s.lower() != "sheet1"]
    sheet_numbers = [int(s.lower().replace("sheet", "")) for s in filtered_sheet_names if s.lower().replace("sheet", "").isdigit()]
    sheet_numbers.sort()
    next_sheet_name = f"Sheet{sheet_numbers[-1] + 1}" if sheet_numbers else "Sheet2"

    # 📌 คำนวณชื่อชีตใหม่ (SheetN+1)
    filtered_sheet_names = [s for s in sheet_names if s.lower() != "sheet1"]
    sheet_numbers = [int(s.lower().replace("sheet", "")) for s in filtered_sheet_names if s.lower().replace("sheet", "").isdigit()]
    sheet_numbers.sort()
    next_sheet_number = sheet_numbers[-1] + 1 if sheet_numbers else 2
    next_sheet_name = f"Sheet{next_sheet_number}"

    # 📦 ปุ่มสร้างชีตใหม่
    if st.button(f"➕ สร้างชีตที่ {next_sheet_name} "):
        try:
            # ใช้ sheet ล่าสุดเป็นต้นแบบ
            last_sheet = f"Sheet{sheet_numbers[-1]}"
            source_ws = sh.worksheet(last_sheet)
            df_prev = source_ws.get_all_values()

            # คัดลอกค่า current
            lower_prev_left  = [[f"={last_sheet}!C{i+3}"] for i in range(24)]  # ซ้าย
            lower_prev_right = [[f"={last_sheet}!E{i+3}"] for i in range(24)]  # ขวา
            upper_prev_left  = [[f"={last_sheet}!H{i+3}"] for i in range(24)]
            upper_prev_right = [[f"={last_sheet}!J{i+3}"] for i in range(24)]

            

            # ตรวจว่าชีตนี้มีอยู่แล้วหรือไม่
            if next_sheet_name.lower() in [ws.title.lower() for ws in sh.worksheets()]:
                st.warning(f"⚠️ Sheet '{next_sheet_name}' มีอยู่แล้ว")
                st.stop()

            # สร้างชีตใหม่
            new_ws = sh.duplicate_sheet(source_sheet_id=source_ws.id, new_sheet_name=next_sheet_name)
            
            sheets = sh.worksheets()
            new_ws = sh.worksheet(next_sheet_name)
            # ย้าย sheet ไปท้ายสุด
            sheets = [ws for ws in sheets if ws.title != next_sheet_name]
            sheets.append(new_ws)
            sh.reorder_worksheets(sheets)

            
                       
                        
            # วางสูตร (ระบุ USER_ENTERED เพื่อให้เป็นสูตร)
            new_ws.update("C3:C26", lower_prev_left, value_input_option="USER_ENTERED")
            new_ws.update("E3:E26", lower_prev_right, value_input_option="USER_ENTERED")
            new_ws.update("H3:H26", upper_prev_left, value_input_option="USER_ENTERED")
            new_ws.update("J3:J26", upper_prev_right, value_input_option="USER_ENTERED")

            
            
            try:
                new_ws.update("C3:C26", lower_prev_left, value_input_option="USER_ENTERED")
                new_ws.update("E3:E26", lower_prev_right, value_input_option="USER_ENTERED")
                new_ws.update("H3:H26", upper_prev_left, value_input_option="USER_ENTERED")
                new_ws.update("J3:J26", upper_prev_right, value_input_option="USER_ENTERED")

            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดขณะใส่สูตร: {e}")


            from gspread.utils import rowcol_to_a1
            
            import time

            for i in range(24):

                if i % 10 == 0:
                    time.sleep(2)



            st.session_state["selected_sheet_auto"] = next_sheet_name  # ✅ เพิ่มบรรทัดนี้
            st.success(f"✅ สร้างชีต '{next_sheet_name}' สำเร็จแล้ว 🎉")
            st.rerun()
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")


    # ✅ โหลดค่าทันทีจาก selected_sheet และป้องกัน error
    ws = sh.worksheet(selected_sheet)
    df_prev = ws.get_all_values()

    def get_value(row, index):
        return row[index] if len(row) > index else ""

    rows = df_prev[2:34]  # ดึงแถว 3 ถึง 26 (index เริ่มที่ 0)
    while len(rows) < 24:
        rows.append([""] * 10)  # ถ้ายังไม่ครบ 24 แถว ให้เติมแถวว่าง

    lower_current_left  = [get_value(row, 2) for row in rows]
    lower_current_right = [get_value(row, 4) for row in rows]
    upper_current_left  = [get_value(row, 7) for row in rows]
    upper_current_right = [get_value(row, 9) for row in rows]

    # ✅ ชั่วโมงและวันที่
    try:
        default_hours = float(ws.acell("H1").value or 0)
    except:
        default_hours = 0.0
    default_prev_date = ws.acell("A2").value or ""
    default_curr_date = ws.acell("B2").value or ""

    hours = st.number_input("⏱️ ชั่วโมง", min_value=0.0, step=0.1, value=float(default_hours))
    prev_date = st.text_input("📅 วันที่ตรวจก่อนหน้า", placeholder="DD/MM/YYYY", value=default_prev_date)
    curr_date = st.text_input("📅 วันที่ตรวจล่าสุด", placeholder="DD/MM/YYYY", value=default_curr_date)

    # ✅ LOWER ซ้าย / ขวา
    st.markdown("### 🔧 แปรงถ่าน LOWER ซ้าย / ขวา")
    lower_left = []
    lower_right = []
    cols = st.columns(6)
    for i in range(24):
        col = cols[i % 6]
        with col:
            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ⬅️ ซ้าย</div>", unsafe_allow_html=True)
            default_val_l = lower_current_left[i] if i < len(lower_current_left) else ""
            val_l = st.text_input("", key=f"ll_{i}", value=default_val_l, label_visibility="collapsed")
            lower_left.append(float(val_l) if val_l else 0.0)

            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ➡️ ขวา</div>", unsafe_allow_html=True)
            default_val_r = lower_current_right[i] if i < len(lower_current_right) else ""
            val_r = st.text_input("", key=f"lr_{i}", value=default_val_r, label_visibility="collapsed")
            lower_right.append(float(val_r) if val_r else 0.0)

    # ✅ UPPER ซ้าย / ขวา
    st.markdown("### 🔧 แปรงถ่าน UPPER ซ้าย / ขวา")
    upper_left = []
    upper_right = []
    cols = st.columns(6)
    for i in range(24):
        col = cols[i % 6]
        with col:
            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ⬅️ ซ้าย</div>", unsafe_allow_html=True)
            default_val_l = upper_current_left[i] if i < len(upper_current_left) else ""
            val_l = st.text_input("", key=f"ul_{i}", value=default_val_l, label_visibility="collapsed")
            upper_left.append(float(val_l) if val_l else 0.0)

            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ➡️ ขวา</div>", unsafe_allow_html=True)
            default_val_r = upper_current_right[i] if i < len(upper_current_right) else ""
            val_r = st.text_input("", key=f"ur_{i}", value=default_val_r, label_visibility="collapsed")
            upper_right.append(float(val_r) if val_r else 0.0)
        





    # โหลดชั่วโมง/วัน
    try:
        default_hours = float(ws.acell("H1").value or 0)
    except:
        default_hours = 0.0
    default_prev_date = ws.acell("A2").value or ""
    default_curr_date = ws.acell("B2").value or ""


    hours = st.number_input("⏱️ ชั่วโมง", min_value=0.0, step=0.1, value=float(default_hours))
    
    prev_date = st.text_input("📅 วันที่ตรวจก่อนหน้า", placeholder="DD/MM/YYYY", value=default_prev_date)
    curr_date = st.text_input("📅 วันที่ตรวจล่าสุด", placeholder="DD/MM/YYYY", value=default_curr_date)

 
    
    

    

    st.markdown("### 🔧 แปรงถ่าน LOWER ซ้าย / ขวา")
    lower_left = []
    lower_right = []
    cols = st.columns(6)
    for i in range(24):
        col = cols[i % 6]
        with col:
            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ⬅️ ซ้าย</div>", unsafe_allow_html=True)
            val_l = st.text_input("", key=f"ll_{i}", value="", label_visibility="collapsed")
            lower_left.append(float(val_l) if val_l else 0.0)

            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ➡️ ขวา</div>", unsafe_allow_html=True)
            val_r = st.text_input("", key=f"lr_{i}", value="", label_visibility="collapsed")
            lower_right.append(float(val_r) if val_r else 0.0)


    # ------------------ 🔧 UPPER ------------------
    st.markdown("### 🔧 แปรงถ่าน UPPER ซ้าย / ขวา")
    upper_left = []
    upper_right = []
    cols = st.columns(6)
    for i in range(24):
        col = cols[i % 6]
        with col:
            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ⬅️ ซ้าย</div>", unsafe_allow_html=True)
            val_l = st.text_input("", key=f"ul_{i}", value="", label_visibility="collapsed")
            upper_left.append(float(val_l) if val_l else 0.0)

            st.markdown(f"<div style='text-align: center;'>แปรง {i+1} ➡️ ขวา</div>", unsafe_allow_html=True)
            val_r = st.text_input("", key=f"ur_{i}", value="", label_visibility="collapsed")
            upper_right.append(float(val_r) if val_r else 0.0)
            
 





 
