import streamlit as st
import json
import pandas as pd
from datetime import datetime

DATA_FILE = "attendance_data.json"

# --- Utility Functions ---
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

def delete_student(data, name):
    if name in data:
        del data[name]
        save_data(data)
        st.success(f"Student '{name}' deleted.")
    else:
        st.error("Student not found.")

def mark_attendance(data, name, status, date_str):
    if name in data:
        data[name][date_str] = status
        save_data(data)
        st.success(f"Marked {status} for {name} on {date_str}.")
    else:
        st.error("Student not found!")

def generate_summary(data):
    summary = {}
    for student, records in data.items():
        p = sum(1 for val in records.values() if val == "P")
        a = sum(1 for val in records.values() if val == "A")
        summary[student] = {"Present": p, "Absent": a}
    return summary

# --- Streamlit UI ---
st.set_page_config(page_title="Student Attendance", layout="centered")
st.title("📘 Student Attendance System")

menu = st.sidebar.radio("Menu", ["Add Student", "Mark Attendance", "View Summary", "Delete Student"])
data = load_data()

# Add Student
if menu == "Add Student":
    name = st.text_input("Enter new student name")
    if st.button("Add Student"):
        add_student(data, name)

# Delete Student
elif menu == "Delete Student":
    if data:
        student = st.selectbox("Select student to delete", list(data.keys()))
        if st.button("Delete"):
            delete_student(data, student)
    else:
        st.warning("No students to delete.")

# Mark Attendance
elif menu == "Mark Attendance":
    if data:
        student = st.selectbox("Select student", list(data.keys()))
        status = st.radio("Select status", ["P", "A"])
        selected_date = st.date_input("Select date", datetime.today())
        date_str = selected_date.strftime("%Y-%m-%d")

        if st.button("Mark Attendance"):
            mark_attendance(data, student, status, date_str)
    else:
        st.warning("Please add students first.")

# View Summary
elif menu == "View Summary":
    st.header("📊 Attendance Summary")
    summary = generate_summary(data)

    if summary:
        df = pd.DataFrame.from_dict(summary, orient='index')
        df.index.name = "Student"
        df.reset_index(inplace=True)

        # Calculate percentage
        df["Total"] = df["Present"] + df["Absent"]
        df["% Attendance"] = (df["Present"] / df["Total"]) * 100
        df.fillna(0, inplace=True)  # Handle division by zero

        st.dataframe(df[["Student", "Present", "Absent", "% Attendance"]])

        # Plot bar chart with attendance %
        st.bar_chart(df.set_index("Student")[["% Attendance"]])
    else:
        st.info("No attendance records to summarize yet.")


        st.dataframe(df)
        st.bar_chart(df.set_index("Student"))
    else:
        st.info("No attendance records to summarize yet.")
