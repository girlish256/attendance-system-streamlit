import streamlit as st
import json
from datetime import datetime

DATA_FILE = "attendance_data.json"

# Defined Funtiones for the system
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_student(data, name):
    if name and name not in data:
        data[name] = {}
        save_data(data)
        st.success(f"Student '{name}' added.")
    elif name in data:
        st.warning("Student already exists.")
    else:
        st.error("Please enter a valid name.")

def mark_attendance(data, name, status):
    if name in data:
        today = datetime.today().strftime("%Y-%m-%d")
        data[name][today] = status
        save_data(data)
        st.success(f"Marked {status} for {name} on {today}.")
    else:
        st.error("Student not found!")

def generate_summary(data):
    summary = {}
    for student, records in data.items():
        p = sum(1 for val in records.values() if val == "P")
        a = sum(1 for val in records.values() if val == "A")
        summary[student] = {"Present": p, "Absent": a}
    return summary

# UI from here
st.title("📘 Student Attendance System")

menu = st.sidebar.radio("Menu", ["Add Student", "Mark Attendance", "View Summary"])
data = load_data()

if menu == "Add Student":
    name = st.text_input("Enter new student name")
    if st.button("Add"):
        add_student(data, name)

elif menu == "Mark Attendance":
    if data:
        student = st.selectbox("Select student", list(data.keys()))
        status = st.radio("Status", ["P", "A"])
        if st.button("Mark"):
            mark_attendance(data, student, status)
    else:
        st.warning("No students found. Please add students first.")

elif menu == "View Summary":
    st.header("📊 Attendance Summary")
    summary = generate_summary(data)
    st.table(summary)
