import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from collections import defaultdict

DATA_FILE = "attendance_data.json"

# Utility Functions
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

# Streamlit UI
st.set_page_config(page_title="Student Attendance", layout="centered")
st.title("📘 Student Attendance System")

menu = st.sidebar.radio("Menu", ["Add Student", "Mark Attendance", "View Summary", "Delete Student"])
data = load_data()

if menu == "Add Student":
    name = st.text_input("Enter new student name")
    if st.button("Add Student"):
        add_student(data, name)

elif menu == "Delete Student":
    if data:
        student = st.selectbox("Select student to delete", list(data.keys()))
        if st.button("Delete"):
            delete_student(data, student)
    else:
        st.warning("No students to delete.")

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

elif menu == "View Summary":
    st.header("📊 Attendance Summary")
    summary = generate_summary(data)

    if summary:
        df = pd.DataFrame.from_dict(summary, orient='index')
        df.index.name = "Student"
        df.reset_index(inplace=True)

        # Calculate attendance percentage
        df["Total"] = df["Present"] + df["Absent"]
        df["% Attendance"] = (df["Present"] / df["Total"]) * 100
        df.fillna(0, inplace=True)

        # Display table
        st.dataframe(df[["Student", "Present", "Absent", "% Attendance"]])

        # Bar Chart with different colors
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df["Student"],
            y=df["% Attendance"],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'] * len(df),
            text=df["% Attendance"].round(1),
            textposition='auto'
        ))
        fig1.update_layout(
            title="📊 Percentage Attendance per Student",
            yaxis_title="% Attendance",
            xaxis_title="Student",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Line Chart (Present vs Absent by Date)
        daily_counts = defaultdict(lambda: {'P': 0, 'A': 0})
        for records in data.values():
            for date, status in records.items():
                daily_counts[date][status] += 1

        daily_df = pd.DataFrame([
            {"Date": d, "Present": v["P"], "Absent": v["A"]}
            for d, v in sorted(daily_counts.items())
        ])
        daily_df["Date"] = pd.to_datetime(daily_df["Date"])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily_df["Date"], y=daily_df["Present"],
            mode='lines+markers', name='Present', line=dict(color='green')
        ))
        fig2.add_trace(go.Scatter(
            x=daily_df["Date"], y=daily_df["Absent"],
            mode='lines+markers', name='Absent', line=dict(color='red')
        ))
        fig2.update_layout(
            title="📈 Daily Attendance (Present vs Absent)",
            xaxis_title="Date",
            yaxis_title="Count",
            height=450
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No attendance records to summarize yet.")

