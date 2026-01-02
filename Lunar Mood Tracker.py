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

# Mood definitions: (label, emoji, value, color)
MOODS = [
    ("F", "😞", 0, "#FF4C4C"),
    ("D", "😕", 1, "#FF884C"),
    ("C", "😐", 2, "#FFD24C"),
    ("B", "🙂", 3, "#A4DE02"),
    ("A", "😄", 4, "#32CD32"),
    ("A+", "🤩", 5, "#008000"),
]

MOOD_MAP = {m[0]: m[2] for m in MOODS}
COLOR_MAP = {m[2]: m[3] for m in MOODS}

START_DATE = dt.date(2026, 1, 1)
END_DATE = dt.date(2026, 12, 31)

# -----------------------
# Load or create CSV
# -----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["date"])
        # Fill missing columns if upgrading old CSV
        if "note" not in df.columns:
            df["note"] = ""
        if "anxiety" not in df.columns:
            df["anxiety"] = None
    else:
        dates = pd.date_range(START_DATE, END_DATE)
        df = pd.DataFrame({
            "date": dates,
            "mood": [None] * len(dates),
            "note": [""] * len(dates),
            "anxiety": [None] * len(dates)
        })
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
st.title("Luna Tracker")
st.caption("Giggly :) , colorful mood tracker with notes & anxiety level")

# -----------------------
# Date selection
# -----------------------
selected_date = st.date_input(
    "Select Date",
    value=dt.date.today() if dt.date.today().year == 2026 else START_DATE,
    min_value=START_DATE,
    max_value=END_DATE
)

# -----------------------
# Mood buttons
# -----------------------
st.subheader("How was your day?")

cols = st.columns(len(MOODS))
for col, (label, emoji, value, color) in zip(cols, MOODS):
    with col:
        if st.button(f"{emoji}\n{label}", use_container_width=True):
            df.loc[df["date"] == pd.Timestamp(selected_date), "mood"] = value
            save_data(df)
            st.success("Mood saved!")

# -----------------------
# Daily note input
# -----------------------
st.subheader("Daily note")
current_note = df.loc[df["date"] == pd.Timestamp(selected_date), "note"].values[0]
new_note = st.text_area("Write a note for today:", value=current_note)
if st.button("Save Note"):
    df.loc[df["date"] == pd.Timestamp(selected_date), "note"] = new_note
    save_data(df)
    st.success("Note saved!")

# -----------------------
# Anxiety level input
# -----------------------
st.subheader("Anxiety level (1=low, 5=high)")
current_anxiety = df.loc[df["date"] == pd.Timestamp(selected_date), "anxiety"].values[0]
new_anxiety = st.slider("Select your anxiety level:", 1, 5, int(current_anxiety) if pd.notna(current_anxiety) else 3)
if st.button("Save Anxiety"):
    df.loc[df["date"] == pd.Timestamp(selected_date), "anxiety"] = new_anxiety
    save_data(df)
    st.success("Anxiety saved!")

# -----------------------
# Backup CSV button
# -----------------------
st.subheader("Backup your data")
st.download_button(
    "💾 Download CSV Backup",
    df.to_csv(index=False).encode('utf-8'),
    file_name="mood_2026_backup.csv",
    mime="text/csv"
)

# -----------------------
# Monthly calendar overview
# -----------------------
st.divider()
st.subheader("Monthly Mood Overview")

month = st.selectbox(
    "Select Month",
    range(1, 13),
    format_func=lambda m: calendar.month_name[m]
)

month_df = df[df["date"].dt.month == month].copy()
month_df["day"] = month_df["date"].dt.day

fig, ax = plt.subplots(figsize=(12, 2))
ax.set_xlim(0.5, 31.5)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title(f"{calendar.month_name[month]} 2026", fontsize=16, fontweight="bold")

for _, row in month_df.dropna(subset=["mood"]).iterrows():
    ax.scatter(
        row["day"],
        0.5,
        s=400,
        color=COLOR_MAP[int(row["mood"])],
        edgecolors="black"
    )

st.pyplot(fig)

# -----------------------
# Year summary
# -----------------------
st.divider()
st.subheader("Year Summary")

valid = df.dropna(subset=["mood"])
if not valid.empty:
    avg_mood = valid["mood"].mean()
    avg_anxiety = valid["anxiety"].mean() if "anxiety" in valid.columns else None
    st.metric("Average mood", f"{avg_mood:.2f} / 5")
    if avg_anxiety:
        st.metric("Average anxiety", f"{avg_anxiety:.2f} / 5")

    counts = valid["mood"].value_counts().sort_index()
    fig2, ax2 = plt.subplots()
    ax2.bar(
        counts.index.astype(str),
        counts.values,
        color=[COLOR_MAP[i] for i in counts.index]
    )
    ax2.set_xlabel("Mood")
    ax2.set_ylabel("Days")
    ax2.set_title("Mood distribution 2026")
    st.pyplot(fig2)
else:
    st.info("No data yet")