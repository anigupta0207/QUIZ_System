import streamlit as st
import json
import os
import pandas as pd

# ---------- File Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "..", "users.json")
SCORES_FILE = os.path.join(BASE_DIR, "user_scores.json")

# ---------- Helper Functions ----------
def load_json(file_path):
    """Safely load JSON data."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(file_path, data):
    """Save data to JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- Admin Dashboard ----------
def show_admin_dashboard():
    st.set_page_config(page_title="Admin Dashboard", page_icon="👑", layout="centered")
    st.title("👑 Admin Dashboard")
    st.write("Welcome, Admin!")

    # Load users and scores
    users = load_json(USERS_FILE)
    user_scores = load_json(SCORES_FILE)

    # --- Registered Users ---
    st.subheader("👥 Registered Users")
    if users:
        for username, info in users.items():
            st.write(f"👤 **{username}** — Role: {info.get('role', 'user')}")
    else:
        st.info("No users found.")

    st.divider()

    # --- Student Scores & Ranking ---
    st.subheader("📊 Student Scores and Rankings")

    if not user_scores:
        st.info("No student scores available yet.")
    else:
        records = []
        for user, quizzes in user_scores.items():
            for quiz_id, quiz_info in quizzes.items():
                records.append({
                    "Username": user,
                    "Quiz Title": quiz_info.get("quiz_title", "Unknown Quiz"),
                    "Score": quiz_info.get("score", 0),
                    "Completed At": quiz_info.get("completed_at", "N/A")
                })

        if records:
            df = pd.DataFrame(records)
            df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True)

            # Top performers
            st.subheader("🏆 Top Performers")
            top3 = df.head(3)
            for i, row in top3.iterrows():
                st.write(f"**{i}. {row['Username']}** — {row['Score']} points ({row['Quiz Title']})")
        else:
            st.info("No student scores available yet.")

    st.divider()

    # --- Manage Users ---
    st.subheader("🧑‍💻 Manage Users")

    deletable_users = [u for u in users if u.lower() != "admin"]
    if deletable_users:
        user_to_delete = st.selectbox("Select a user to delete", deletable_users, key="delete_user")
        if st.button("🗑️ Delete User"):
            del users[user_to_delete]
            save_json(USERS_FILE, users)
            st.success(f"User '{user_to_delete}' deleted.")
            st.rerun()
    else:
        st.info("No users available to delete.")

    promotable_users = [u for u, info in users.items() if info.get("role") == "user"]
    if promotable_users:
        user_to_promote = st.selectbox("Select a user to promote to admin", promotable_users, key="promote_user")
        if st.button("⬆️ Promote to Admin"):
            users[user_to_promote]["role"] = "admin"
            save_json(USERS_FILE, users)
            st.success(f"User '{user_to_promote}' promoted to admin.")
            st.rerun()
    else:
        st.info("No users available to promote.")

    # --- Logout ---
    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.success("Logged out successfully.")
        st.rerun()
