import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

os.system('pip install openpyxl')

import streamlit as st
import pandas as pd
# ... (rest of your imports)

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="WorkLog Pro", page_icon="📝", layout="wide")

STUDENT_FILE = "data/students.csv"
FACULTY_FILE = "data/faculty.csv"

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def save_data(file_path, data_dict):
    df = pd.DataFrame([data_dict])
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', header=False, index=False)

def get_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 WorkLog Navigation")
role = st.sidebar.radio("Select Your Role:", ["Student Portal", "Faculty Portal"])

# --- STUDENT PORTAL ---
if role == "Student Portal":
    st.title("👨‍🎓 Student Work Register")
    st.info("Please fill in your details. Date and Time are automatically recorded.")
    
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            reg_no = st.text_input("Register Number")
        with col2:
            name = st.text_input("Full Name")
        
        task = st.text_area("Task Description", placeholder="What did you work on today?")
        
        submit = st.form_submit_button("Submit Entry")
        
        if submit:
            if reg_no and name and task:
                new_entry = {
                    "Register_No": reg_no,
                    "Name": name,
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Task": task
                }
                save_data(STUDENT_FILE, new_entry)
                st.success(f"Log saved successfully for {name}!")
            else:
                st.error("Please fill in all fields.")

# --- FACULTY PORTAL ---
else:
    st.title("👩‍🏫 Faculty Dashboard")
    
    # Simple Role-Based Access Control (Password)
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        with st.container():
            st.subheader("Faculty Authentication")
            user_id = st.text_input("Faculty ID")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if user_id == "admin" and password == "teacher123":
                    st.session_state['authenticated'] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    else:
        # Logout button in sidebar
        if st.sidebar.button("Logout"):
            st.session_state['authenticated'] = False
            st.rerun()

        # Faculty Log Entry Section
        with st.expander("➕ Log Your Own Faculty Activity"):
            with st.form("faculty_form", clear_on_submit=True):
                emp_id = st.text_input("Employee ID")
                f_task = st.text_area("Activity Description")
                f_submit = st.form_submit_button("Save Faculty Log")
                if f_submit:
                    f_entry = {
                        "Emp_ID": emp_id,
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Task": f_task
                    }
                    save_data(FACULTY_FILE, f_entry)
                    st.success("Your activity has been logged.")

        st.divider()

        # Student Monitoring Section
        st.subheader("📊 Monitor Student Performance")
        student_df = get_data(STUDENT_FILE)
        
        if not student_df.empty:
            # Sorting by Newest First
            student_df = student_df.sort_values(by=["Date", "Time"], ascending=False)
            
            # Search/Filter functionality
            search = st.text_input("🔍 Search by Register No or Name")
            if search:
                student_df = student_df[student_df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
            
            # Display Table
            st.dataframe(student_df, use_container_width=True)

            # Export to Excel (.xlsx) logic
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                student_df.to_excel(writer, index=False, sheet_name='StudentLogs')
            
            st.download_button(
                label="📥 Download Student Report (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"Student_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No student logs found yet.")