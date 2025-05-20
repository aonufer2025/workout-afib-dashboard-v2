
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🏋️‍♂️ Workouts & 🫀 AFib Events Dashboard (2025)")

# Load data
df = pd.read_csv("cleaned_workouts_with_afib_2025_filtered.csv", parse_dates=["workout_start", "first_afib", "last_afib"])
df["date"] = df["workout_start"].dt.date

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", [df["workout_start"].min(), df["workout_start"].max()])
workout_types = st.sidebar.multiselect("Workout Types", options=df["workout_type"].dropna().unique(), default=list(df["workout_type"].dropna().unique()))

# Filter data
if len(date_range) == 2:
    df = df[(df["workout_start"].dt.date >= date_range[0]) & (df["workout_start"].dt.date <= date_range[1])]
df = df[df["workout_type"].isin(workout_types)]

# Daily summary
summary = df.groupby("date").agg(
    workouts=("workout_type", "count"),
    avg_hr=("avg_hr", "mean"),
    max_hr=("max_hr", "mean"),
    total_duration=("duration_min", "sum"),
    total_calories=("calories", "sum"),
    avg_output=("total_output_kj", "mean"),
    avg_percentile=("leaderboard_percentile", "mean"),
    afib_events=("afib_events", "sum")
).fillna(0).reset_index()

# Charts
st.subheader("📊 Daily Summary")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Workouts", int(summary['workouts'].sum()))
    st.bar_chart(summary.set_index("date")[["workouts"]])

with col2:
    st.metric("Total AFib Events", int(summary['afib_events'].sum()))
    st.bar_chart(summary.set_index("date")[["afib_events"]])

col3, col4 = st.columns(2)
with col3:
    st.subheader("🔥 Calories Burned")
    st.line_chart(summary.set_index("date")[["total_calories"]])

with col4:
    st.subheader("⚡ Output (kJ)")
    st.line_chart(summary.set_index("date")[["avg_output"]])

col5, col6 = st.columns(2)
with col5:
    st.subheader("🏅 Leaderboard Percentile")
    st.line_chart(summary.set_index("date")[["avg_percentile"]])

with col6:
    st.subheader("🕒 Workout Duration")
    st.line_chart(summary.set_index("date")[["total_duration"]])

# Workout type distribution
st.subheader("🧘 Workout Type Distribution")
type_counts = df["workout_type"].value_counts()
st.bar_chart(type_counts)
