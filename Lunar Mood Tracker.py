import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# -----------------------
# Basic app settings
# -----------------------
st.set_page_config(
    page_title="Mood Tracker 2026",
    layout="wide"
)

# Mood grades mapped to numbers
MOOD_SCALE = {
    "F": 0,
    "D": 1,
    "C": 2,
    "B": 3,
    "A": 4,
    "A+": 5
}

# Colors from bad (red) to good (green)
MOOD_COLORS = {
    0: "#8b0000",
    1: "#ff4500",
    2: "#ffa500",
    3: "#9acd32",
    4: "#32cd32",
    5: "#006400"
}

START_DATE = dt.date(2026, 1, 1)
END_DATE = dt.date(2026, 12, 31)

# -----------------------
# Create yearly data
# -----------------------
if "data" not in st.session_state:
    dates = pd.date_range(START_DATE, END_DATE)
    st.session_state.data = pd.DataFrame({
        "date": dates,
        "mood": [None] * len(dates)
    })

df = st.session_state.data

# -----------------------
# Header
# -----------------------
st.title("Mood Tracker – 2026")

# -----------------------
# Daily input
# -----------------------
col1, col2 = st.columns(2)

with col1:
    selected_date = st.date_input(
        "Select date",
        value=START_DATE,
        min_value=START_DATE,
        max_value=END_DATE
    )

with col2:
    selected_mood = st.selectbox(
        "Mood grade",
        list(MOOD_SCALE.keys())
    )

if st.button("Save"):
    df.loc[df["date"] == pd.Timestamp(selected_date), "mood"] = MOOD_SCALE[selected_mood]
    st.success("Saved")

# -----------------------
# Calendar-style view
# -----------------------
st.subheader("Year overview")

df_plot = df.copy()
df_plot["week"] = df_plot["date"].dt.isocalendar().week
df_plot["weekday"] = df_plot["date"].dt.weekday

fig, ax = plt.subplots(figsize=(18, 4))

for _, row in df_plot.dropna().iterrows():
    ax.scatter(
        row["week"],
        row["weekday"],
        s=120,
        color=MOOD_COLORS[int(row["mood"])]
    )

ax.set_yticks(range(7))
ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
ax.set_xlabel("Week of year")
ax.set_title("Mood calendar – 2026")
ax.invert_yaxis()

st.pyplot(fig)

# -----------------------
# Year summary
# -----------------------
st.subheader("Year summary")

valid_days = df.dropna()

if not valid_days.empty:
    average = valid_days["mood"].mean()
    good_days = (valid_days["mood"] >= 4).sum()
    bad_days = (valid_days["mood"] <= 1).sum()

    st.write(f"Average mood: {average:.2f} / 5")
    st.write(f"Good days (A, A+): {good_days}")
    st.write(f"Bad days (D, F): {bad_days}")

    if average >= 4:
        st.success("Overall: Very good year")
    elif average >= 2.5:
        st.info("Overall: Average year")
    else:
        st.warning("Overall: Tough year")
else:
    st.info("No data yet")