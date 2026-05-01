import streamlit as st
import pickle
import sqlite3
import pandas as pd
import plotly.express as px

from database.db import (
    init_db, insert_log, insert_user, check_user,
    save_profile, load_profile
)

from utils.recommendations import get_recommendation
from utils.chatbot import ai_chat

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MindMitra", page_icon="🧠", layout="wide")

# ---------------- CUSTOM CSS (🔥 PREMIUM UI) ----------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
}

.metric-card {
    background: linear-gradient(135deg,#6366f1,#7c3aed);
    padding: 20px;
    border-radius: 16px;
    color: white;
    text-align:center;
}

h1, h2, h3 {
    color: white;
}

.stButton>button {
    background: linear-gradient(135deg,#6366f1,#7c3aed);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
init_db()

with open('model/model.pkl', 'rb') as f:
    model, le_mood, le_activity, le_stress = pickle.load(f)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.title("🧠 MindMitra")
    st.caption("Your child’s mental wellness companion")

    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        st.subheader("Sign Up")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if insert_user(new_user, new_pass):
                st.success("Account created")
            else:
                st.error("Username exists")

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🧠 MindMitra")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📊 Dashboard", "🤖 Chatbot"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- HOME ----------------
if page == "🏠 Home":

    st.title("👋 Welcome Back")

    col1, col2 = st.columns(2)

    # -------- PROFILE CARD --------
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👶 Child Profile")

        username = st.session_state.username
        profile = load_profile(username)

        if profile:
            name, age, grade = profile

            st.write(f"**Name:** {name}")
            st.write(f"**Age:** {age}")
            st.write(f"**Grade:** {grade}")

        else:
            name = st.text_input("Name")
            age = st.slider("Age", 5, 15, 10)
            grade = st.selectbox("Grade", ["1-5", "6-8", "9-10"])

            if st.button("Save Profile"):
                save_profile(username, name, age, grade)
                st.success("Saved")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- CHECK CARD --------
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("😊 Daily Check")

        mood_display = st.selectbox(
            "Mood", ["happy 😊", "sad 😢", "angry 😡"]
        )

        activity = st.selectbox(
            "Activity Level", ["low", "medium", "high"]
        )

        sleep = st.slider("Sleep", 0, 12, 7)
        screen = st.slider("Screen Time", 0, 10, 3)

        mood = mood_display.split()[0]

        if st.button("Analyze"):
            mood_enc = le_mood.transform([mood])[0]
            activity_enc = le_activity.transform([activity])[0]

            prediction = model.predict(
                [[mood_enc, sleep, screen, activity_enc]]
            )

            stress = le_stress.inverse_transform(prediction)[0]

            st.success(f"Stress Level: {stress}")
            st.info(get_recommendation(stress))

            insert_log(mood, sleep, screen, activity, stress)

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if page == "📊 Dashboard":

    st.title("📊 Analytics")

    conn = sqlite3.connect('mindmitra.db')
    df = pd.read_sql("SELECT * FROM logs", conn)

    if not df.empty:

        stress_map = {"low":1,"medium":2,"high":3}
        df["stress_score"] = df["stress"].map(stress_map)
        df["entry"] = range(1,len(df)+1)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f'<div class="metric-card">Entries<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card">Avg Stress<br><h2>{round(df["stress_score"].mean(),2)}</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card">Top Mood<br><h2>{df["mood"].mode()[0]}</h2></div>', unsafe_allow_html=True)

        st.markdown("---")

        # LINE
        fig1 = px.line(df, x="entry", y="stress_score", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        # DONUT
        fig2 = px.pie(df, names="stress", hole=0.6)
        st.plotly_chart(fig2, use_container_width=True)

        # BAR
        mood_counts = df["mood"].value_counts().reset_index()
        mood_counts.columns = ["Mood","Count"]

        fig3 = px.bar(mood_counts, x="Mood", y="Count", color="Mood")
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("No data yet")

# ---------------- CHATBOT ----------------
if page == "🤖 Chatbot":

    st.title("🤖 Wellness Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Talk to me...")

    if st.button("Send") and user_input:
        response = ai_chat(user_input)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", response))

    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")