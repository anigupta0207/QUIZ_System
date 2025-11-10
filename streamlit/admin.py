import streamlit as st
import json
import os
import pandas as pd
import altair as alt
import csv


# ---------- File Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "..", "users.json")
SCORES_FILE = os.path.join(BASE_DIR, "user_scores.json")


def save_to_csv(username, quiz_id, quiz_title, score, timestamp):
    csv_path = "scores.csv"

    # Create file with header if not exists
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header once
        if not file_exists:
            writer.writerow(["username", "quiz_id", "quiz_title", "score", "timestamp"])

        # Write row
        writer.writerow([username, quiz_id, quiz_title, score, timestamp])


# ---------- Helper Functions ----------
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- Admin Dashboard ----------
def show_admin_dashboard():
    st.set_page_config(page_title="Admin Dashboard", page_icon="👑", layout="wide")

    st.markdown("""
        <style>
        .admin-title {
            font-size: 40px;
            font-weight: 800;
            padding-bottom: 10px;
        }
        .sub-heading {
            font-size: 26px;
            font-weight: 600;
            margin-top: 30px;
        }
        .card {
            background: rgba(255,255,255,0.08);
            padding: 25px;
            border-radius: 18px;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            transition: 0.3s;
            margin-bottom: 20px;
        }
        .card:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.35);
        }
        .mini-card {
            background: rgba(255,255,255,0.05);
            padding: 12px 18px;
            border-radius: 12px;
            margin: 6px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='admin-title'>👑 Admin Dashboard</div>", unsafe_allow_html=True)
    st.write("Welcome, Admin!")

    users = load_json(USERS_FILE)
    user_scores = load_json(SCORES_FILE)

    # ---------- TOP STATS ----------
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f"<div class='card'><h3>Total Users</h3><h2>{len(users)}</h2></div>", unsafe_allow_html=True)
    with colB:
        total_attempts = sum(len(q) for q in user_scores.values()) if user_scores else 0
        st.markdown(f"<div class='card'><h3>Total Quiz Attempts</h3><h2>{total_attempts}</h2></div>", unsafe_allow_html=True)
    with colC:
        admin_count = sum(1 for info in users.values() if info.get("role") == "admin")
        st.markdown(f"<div class='card'><h3>Total Admins</h3><h2>{admin_count}</h2></div>", unsafe_allow_html=True)

    # ---------- REGISTERED USERS ----------
    st.markdown("<div class='sub-heading'>👥 Registered Users</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if users:
        for username, info in users.items():
            st.markdown(
                f"<div class='mini-card'><b>{username}</b> — {info.get('role','user').title()}</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No users found.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SCORES ----------
    st.markdown("<div class='sub-heading'>📊 Student Scores & Ranking</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if not user_scores:
        st.info("No student scores available yet.")
    else:
        records = []
        for user, quizzes in user_scores.items():
            for quiz_id, q in quizzes.items():
                records.append({
                    "Username": user,
                    "Subject": q.get("subject", "Unknown"),
                    "Quiz Title": q.get("quiz_title", "Unknown"),
                    "Score": q.get("score", 0),
                    "Completed At": q.get("completed_at", "N/A")
                })

        df = pd.DataFrame(records).sort_values(by="Score", ascending=False).reset_index(drop=True)
        df.index += 1

        st.dataframe(df, use_container_width=True)

        # ---------- TOP 3 ----------
        st.markdown("<br><h4>🏆 Top Performers</h4>", unsafe_allow_html=True)
        top3 = df.head(3)
        for i, row in top3.iterrows():
            st.write(f"**{i}. {row['Username']}** — {row['Score']} points ({row['Quiz Title']})")

        # ---------- ALTair PIE CHART ----------
        st.markdown("<br><h4>📈 Subject Attempt Distribution</h4>", unsafe_allow_html=True)

        subject_counts = df["Subject"].value_counts().reset_index()
        subject_counts.columns = ["Subject", "Attempts"]

        pie_chart = alt.Chart(subject_counts).mark_arc(innerRadius=50).encode(
            theta="Attempts:Q",
            color="Subject:N",
            tooltip=["Subject", "Attempts"]
        ).properties(
            width=400,
            height=400
        )

        st.altair_chart(pie_chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- MANAGE USERS ----------
    st.markdown("<div class='sub-heading'>🧑‍💻 Manage Users</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Delete Users
    with col1:
        st.subheader("Delete User")
        deletable = [u for u in users if u.lower() != "admin"]
        if deletable:
            user_to_delete = st.selectbox("Select user", deletable)
            if st.button("🗑️ Delete User"):
                del users[user_to_delete]
                save_json(USERS_FILE, users)
                st.success(f"User '{user_to_delete}' deleted.")
                st.rerun()
        else:
            st.info("No users to delete.")

    # Promote Users
    with col2:
        st.subheader("Promote to Admin")
        promotable = [u for u, info in users.items() if info.get("role") == "user"]
        if promotable:
            user_to_promote = st.selectbox("Choose user", promotable)
            if st.button("⬆️ Promote User"):
                users[user_to_promote]["role"] = "admin"
                save_json(USERS_FILE, users)
                st.success(f"User '{user_to_promote}' promoted!")
                st.rerun()
        else:
            st.info("No users available to promote.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- LOGOUT ----------
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
