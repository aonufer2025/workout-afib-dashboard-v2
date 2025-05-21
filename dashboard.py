import streamlit as st
import pandas as pd
import altair as alt

# Load the enriched workout data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_workouts_with_afib_2025_filtered.csv", parse_dates=["start", "end"], low_memory=False)
    df = df[df["start"].dt.year == 2025]  # Only show 2025 workouts
    return df

df = load_data()

st.title("🏋️‍♂️ Workout & Heart Rate Dashboard (2025)")

# Sidebar: filters
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start date", df["start"].min().date())
end_date = st.sidebar.date_input("End date", df["start"].max().date())
selected_types = st.sidebar.multiselect("Workout types", df["type"].unique(), default=df["type"].unique())

# Filter data
mask = (
    (df["start"].dt.date >= start_date) &
    (df["start"].dt.date <= end_date) &
    (df["type"].isin(selected_types))
)
df_filtered = df[mask]

st.markdown(f"### {len(df_filtered)} workouts from {start_date} to {end_date}")

# --- Daily stacked workout count ---
daily_counts = df_filtered.groupby([df_filtered["start"].dt.date, "type"]).size().reset_index(name="count")
chart_counts = alt.Chart(daily_counts).mark_bar().encode(
    x=alt.X("start:T", title="Date"),
    y=alt.Y("count:Q", stack="zero", title="Workout Count"),
    color=alt.Color("type:N", legend=alt.Legend(title="Workout Type"))
).properties(title="Daily Workout Count (stacked by type)", width=700)

st.altair_chart(chart_counts, use_container_width=True)

# --- Duration ---
daily_duration = df_filtered.groupby([df_filtered["start"].dt.date, "type"])['duration_min'].sum().reset_index()
chart_duration = alt.Chart(daily_duration).mark_bar().encode(
    x=alt.X("start:T", title="Date"),
    y=alt.Y("duration_min:Q", stack="zero", title="Total Duration (min)"),
    color=alt.Color("type:N", legend=None)
).properties(title="Daily Duration (min)", width=700)

st.altair_chart(chart_duration, use_container_width=True)

# --- Calories ---
if "calories" in df_filtered.columns:
    daily_calories = df_filtered.groupby([df_filtered["start"].dt.date, "type"])['calories'].sum().reset_index()
    chart_calories = alt.Chart(daily_calories).mark_bar().encode(
        x=alt.X("start:T", title="Date"),
        y=alt.Y("calories:Q", stack="zero", title="Total Calories"),
        color=alt.Color("type:N", legend=None)
    ).properties(title="Daily Calories Burned", width=700)

    st.altair_chart(chart_calories, use_container_width=True)

# --- Avg Heart Rate ---
if "avg_hr" in df_filtered.columns:
    df_hr = df_filtered.dropna(subset=["avg_hr"])
    daily_hr = df_hr.groupby([df_hr["start"].dt.date])['avg_hr'].mean().reset_index()
    chart_hr = alt.Chart(daily_hr).mark_line(point=True).encode(
        x=alt.X("start:T", title="Date"),
        y=alt.Y("avg_hr:Q", title="Avg Heart Rate (bpm)")
    ).properties(title="Daily Average Heart Rate", width=700)

    st.altair_chart(chart_hr, use_container_width=True)

# --- Optional: Add table for drill-down ---
with st.expander("Show full workout log"):
    st.dataframe(df_filtered.sort_values("start", ascending=False))
