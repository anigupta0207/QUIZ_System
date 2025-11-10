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
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["username", "quiz_id", "quiz_title", "score", "timestamp"])
        writer.writerow([username, quiz_id, quiz_title, score, timestamp])


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

    # ---------- Mint Theme CSS ----------
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #ecfdf5 0%, #f9fffb 100%);
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: #d1fae5;
    }
    .admin-title {
        font-size: 38px;
        font-weight: 800;
        color: #059669;
        text-align: center;
        padding-bottom: 20px;
    }
    .sub-heading {
        font-size: 30px;
        font-weight: 700;
        color: #059669;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .card {
        background: #ffffff;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #a7f3d0;
        box-shadow: 0 4px 12px rgba(16,185,129,0.15);
        transition: 0.3s;
        margin-bottom: 20px;
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 18px rgba(16,185,129,0.25);
    }
    .mini-card {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border: 1px solid #a7f3d0;
        color: #064e3b;
        font-weight: 500;
    }
    .top-stat {
    text-align: center;
    background: #ffffff;
    padding: 25px;
    border-radius: 16px;
    border: 2px solid #a7f3d0;
    box-shadow: 0 4px 10px rgba(16,185,129,0.12);
    transition: all 0.3s ease-in-out;
}

    /* Neon mint glow on hover */
    .top-stat:hover {
        border-color: #10b981;
        box-shadow:
            0 0 10px rgba(16,185,129,0.4),
            0 0 20px rgba(16,185,129,0.3),
            0 0 30px rgba(16,185,129,0.2),
            0 0 40px rgba(16,185,129,0.15);
        transform: translateY(-5px);
        background: linear-gradient(180deg, #ffffff, #f0fff9);
    }

    h3 {
        color: #059669;
        font-weight: 700;
    }
    h4 {
        color: #10b981;
        font-weight: 600;
    }
    button {
        background-color: #10b981 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 8px 18px !important;
    }
    button:hover {
        background-color: #059669 !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #a7f3d0;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(16,185,129,0.1);
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
                    /* ---------- Fix for Streamlit Selectbox ---------- */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;          /* white background */
        border: 1.5px solid #a7f3d0 !important;        /* mint border */
        border-radius: 10px !important;
        color: #1e293b !important;                     /* dark text */
        transition: 0.3s;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #10b981 !important;              /* emerald hover border */
        box-shadow: 0 0 0 3px rgba(16,185,129,0.2) !important;
    }
    div[data-baseweb="select"] svg {
        color: #059669 !important;                     /* mint arrow color */
    }
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;          /* dropdown background */
        border: 1px solid #a7f3d0 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #ecfdf5 !important;          /* mint hover */
        color: #065f46 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------- Title ----------
    st.markdown("<div class='admin-title'>👑 Admin Dashboard</div>", unsafe_allow_html=True)
    st.write("Welcome, Admin! Manage users and track performance below.")

    users = load_json(USERS_FILE)
    user_scores = load_json(SCORES_FILE)

    # ---------- TOP STATS ----------
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f"<div class='top-stat'><h3>Total Users</h3><h2>{len(users)}</h2></div>", unsafe_allow_html=True)
    with colB:
        total_attempts = sum(len(q) for q in user_scores.values()) if user_scores else 0
        st.markdown(f"<div class='top-stat'><h3>Total Quiz Attempts</h3><h2>{total_attempts}</h2></div>", unsafe_allow_html=True)
    with colC:
        admin_count = sum(1 for info in users.values() if info.get('role') == 'admin')
        st.markdown(f"<div class='top-stat'><h3>Total Admins</h3><h2>{admin_count}</h2></div>", unsafe_allow_html=True)

    # ---------- SCORES ----------
    st.markdown("<div class='sub-heading'>📊 Student Scores & Ranking</div>", unsafe_allow_html=True)

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
        # ---------- Styled Light Table ----------
        st.markdown("""
        <style>
        .light-table thead th {
            background-color: #d1fae5 !important;   /* Mint header */
            color: #064e3b !important;              /* Dark green text */
            font-weight: 600 !important;
            text-align: center !important;
            border-bottom: 2px solid #a7f3d0 !important;
        }
        .light-table tbody td {
            background-color: white !important;
            color: #1e293b !important;
            border-top: 1px solid #a7f3d0 !important;
            text-align: center !important;
            font-size: 15px !important;
            padding: 6px !important;
        }
        .light-table tbody tr:hover td {
            background-color: #ecfdf5 !important;   /* Mint hover */
        }
        </style>
        """, unsafe_allow_html=True)

        # Convert to HTML manually for full control
        table_html = df.to_html(index=True, classes="light-table", border=0)
        st.markdown(f"""
        <div style="
            background:white;
            border:1px solid #a7f3d0;
            border-radius:12px;
            box-shadow:0 4px 10px rgba(16,185,129,0.1);
            padding:10px;
            margin-top:10px;
        ">
        {table_html}
        </div>
        """, unsafe_allow_html=True)



        # ---------- TOP 3 ----------
        st.markdown("<br><h4>🏆 Top Performers</h4>", unsafe_allow_html=True)
        top3 = df.head(3)
        for i, row in top3.iterrows():
            st.write(f"**{i}. {row['Username']}** — {row['Score']} points ({row['Quiz Title']})")

        # ---------- QUIZ RESULT BAR CHARTS BY SUBJECT ----------
        st.markdown("<br><h4>📊 Student Marks by Subject and Level</h4>", unsafe_allow_html=True)

        subjects = ["C", "C++", "Python"]
        difficulty_levels = ["Basic", "Intermediate", "Advanced"]

        # Mint-green color scheme
        level_colors = {
            "Basic": "#bbf7d0",         # light mint
            "Intermediate": "#34d399",  # medium mint
            "Advanced": "#065f46"       # dark emerald
        }

        # Create one chart per subject
        chart_cols = st.columns(3)

        for i, subject in enumerate(subjects):
            subject_df = df[df["Subject"].str.lower() == subject.lower()]

            with chart_cols[i]:
                st.markdown(f"<h5 style='color:#047857; font-weight:700;'>💻 {subject}</h5>", unsafe_allow_html=True)

                if subject_df.empty:
                    st.info(f"No data for {subject}")
                    continue

                # Extract quiz level from quiz title (Basic / Intermediate / Advanced)
                subject_df["Level"] = subject_df["Quiz Title"].apply(
                    lambda x: (
                        "Basic" if "basic" in x.lower()
                        else "Intermediate" if "intermediate" in x.lower()
                        else "Advanced" if "advanced" in x.lower()
                        else "Unknown"
                    )
                )

                # Filter only valid levels
                subject_df = subject_df[subject_df["Level"] != "Unknown"]

                if subject_df.empty:
                    st.info(f"No valid quiz levels for {subject}")
                    continue

                # Build bar chart
                bar_chart = (
                    alt.Chart(subject_df, background="#ffffff")
                    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                    .encode(
                        x=alt.X("Username:N", title="Student Name", sort=alt.SortField("Score", order="descending")),
                        y=alt.Y("Score:Q", title="Marks"),
                        color=alt.Color(
                            "Level:N",
                            scale=alt.Scale(domain=difficulty_levels, range=list(level_colors.values())),
                            legend=alt.Legend(title="Level")
                        ),
                        tooltip=["Username", "Level", "Score", "Quiz Title"]
                    )
                    .properties(width=300, height=300)
                    .configure_axis(
                        gridColor="#e5e7eb",
                        labelColor="#1e293b",
                        titleColor="#047857"
                    )
                    .configure_view(
                        strokeOpacity=0
                    )
                )

                st.altair_chart(bar_chart, use_container_width=False)




    # ---------- MANAGE USERS ----------
    st.markdown("<div class='sub-heading'>🧑‍💻 Manage Users</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

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
