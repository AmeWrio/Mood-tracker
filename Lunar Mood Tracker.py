import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import os
import calendar

# -----------------------
# App config
# -----------------------
st.set_page_config(
    page_title="Mood Tracker 2026",
    layout="wide"
)

DATA_FILE = "mood_2026.csv"

MOODS = [
    ("F", "😞", 0, "#8b0000"),
    ("D", "😕", 1, "#ff4500"),
    ("C", "😐", 2, "#ffa500"),
    ("B", "🙂", 3, "#9acd32"),
    ("A", "😄", 4, "#32cd32"),
    ("A+", "🤩", 5, "#006400"),
]

MOOD_MAP = {m[0]: m[2] for m in MOODS}
COLOR_MAP = {m[2]: m[3] for m in MOODS}

START_DATE = dt.date(2026, 1, 1)
END_DATE = dt.date(2026, 12, 31)

# -----------------------
# Data persistence
# -----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["date"])
    dates = pd.date_range(START_DATE, END_DATE)
    df = pd.DataFrame({"date": dates, "mood": [None] * len(dates)})
    df.to_csv(DATA_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

df = st.session_state.data

# -----------------------
# Header
# -----------------------
st.title("Mood Tracker 2026")
st.caption("Daylio-style daily mood logging")

# -----------------------
# Date selection
# -----------------------
selected_date = st.date_input(
    "Date",
    value=dt.date.today() if dt.date.today().year == 2026 else START_DATE,
    min_value=START_DATE,
    max_value=END_DATE
)

# -----------------------
# Mood buttons (Daylio style)
# -----------------------
st.subheader("How was your day?")

cols = st.columns(len(MOODS))
for col, (label, emoji, value, color) in zip(cols, MOODS):
    with col:
        if st.button(f"{emoji}\n{label}", use_container_width=True):
            df.loc[df["date"] == pd.Timestamp(selected_date), "mood"] = value
            save_data(df)
            st.success("Saved")

# -----------------------
# Monthly calendar view
# -----------------------
st.divider()
st.subheader("Monthly overview")

month = st.selectbox(
    "Month",
    range(1, 13),
    format_func=lambda m: calendar.month_name[m]
)

year_df = df[df["date"].dt.month == month].copy()
year_df["day"] = year_df["date"].dt.day

fig, ax = plt.subplots(figsize=(10, 3))
ax.set_title(calendar.month_name[month])
ax.set_xlim(0.5, 31.5)
ax.set_ylim(0, 1)
ax.axis("off")

for _, row in year_df.dropna().iterrows():
    ax.scatter(
        row["day"],
        0.5,
        s=400,
        color=COLOR_MAP[int(row["mood"])]
    )

st.pyplot(fig)

# -----------------------
# Year summary (Daylio-style stats)
# -----------------------
st.divider()
st.subheader("Year stats")

valid = df.dropna()

if not valid.empty:
    avg = valid["mood"].mean()
    st.metric("Average mood", f"{avg:.2f} / 5")

    counts = valid["mood"].value_counts().sort_index()
    fig2, ax2 = plt.subplots()
    ax2.bar(
        counts.index.astype(str),
        counts.values,
        color=[COLOR_MAP[i] for i in counts.index]
    )
    ax2.set_xlabel("Mood")
    ax2.set_ylabel("Days")
    ax2.set_title("Mood distribution")
    st.pyplot(fig2)
else:
    st.info("No data yet")