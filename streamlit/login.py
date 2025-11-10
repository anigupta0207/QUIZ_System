import streamlit as st
import json
import os
import hashlib

# ---------- Utility Functions ----------

def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def load_scores():
    if not os.path.exists("scores.json"):
        with open("scores.json", "w") as f:
            json.dump({}, f)
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_scores(scores):
    with open("scores.json", "w") as f:
        json.dump(scores, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password, users):
    return username in users and users[username]["password"] == hash_password(password)


# ---------- Streamlit UI ----------

def show_login_system():
    st.set_page_config(
        page_title="PrepSecure",
        page_icon="🎯",
        layout="centered"
    )

    st.title("👩‍💻 Welcome to PrepSecure")

    users = load_users()
    scores = load_scores()

    # Ensure default admin exists
    if "admin" not in users:
        users["admin"] = {
            "password": hash_password("admin123"),
            "role": "admin"
        }
        save_users(users)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "role" not in st.session_state:
        st.session_state.role = ""

    # ------------------- LOGIN / SIGNUP / ADMIN -------------------
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "👨🏻‍💼 Admin Login"])

        # ---------- USER LOGIN ----------
        with tab1:
            st.subheader("Login to your account")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", key="user_login_btn"):
                if verify_user(username, password, users):
                    if users[username]["role"] == "admin":
                        st.warning("Use the Admin Login tab to log in as admin.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = "user"
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                else:
                    st.error("Invalid username or password.")

        # ---------- USER SIGN UP ----------
        with tab2:
            st.subheader("Create a new account")
            new_username = st.text_input("New Username", key="signup_user")
            new_password = st.text_input("New Password", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_conf")

            if st.button("Sign Up", key="signup_btn"):
                if new_username in users:
                    st.warning("Username already exists! Try another.")
                elif new_password != confirm_password:
                    st.warning("Passwords do not match.")
                elif len(new_username) < 3 or len(new_password) < 3:
                    st.warning("Username and password must be at least 3 characters.")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "role": "user"
                    }
                    save_users(users)
                    st.success("Account created successfully! You can now login.")

        # ---------- ADMIN LOGIN ----------
        with tab3:
            st.subheader("Admin Login")
            admin_username = st.text_input("Admin Username", key="admin_user")
            admin_password = st.text_input("Admin Password", type="password", key="admin_pass")

            if st.button("Admin Login", key="admin_login_btn"):
                if verify_user(admin_username, admin_password, users):
                    if users[admin_username]["role"] == "admin":
                        st.session_state.logged_in = True
                        st.session_state.username = admin_username
                        st.session_state.role = "admin"
                        st.success(f"Welcome Admin, {admin_username}!")
                        st.rerun()
                    else:
                        st.error("Access denied: You are not an admin.")
                else:
                    st.error("Invalid admin credentials.")

    # ------------------- AFTER LOGIN -------------------
    else:
        if st.session_state.role == "admin":
            st.success(f"👑 Logged in as Admin: {st.session_state.username}")
            st.header("📊 Admin Dashboard")

            # Registered Users
            st.write("### Registered Users")
            if users:
                for u, info in users.items():
                    st.write(f"👤 **{u}** — Role: {info['role']}")
            else:
                st.write("No users found.")

            # Student Scores
            st.divider()
            st.subheader("Student Scores and Attempts")

            if scores:
                ranked_students = sorted(scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
                st.write(f"| Rank | Student | Score | Attempts |")
                st.write(f"|-------|---------|-------|----------|")
                rank = 1
                for student, data in ranked_students:
                    score = data.get("score", 0)
                    attempts = data.get("attempts", 0)
                    st.write(f"| {rank} | {student} | {score} | {attempts} |")
                    rank += 1
            else:
                st.write("No student score data available.")

            # Manage Users
            st.divider()
            st.subheader("Manage Users")

            deletable_users = [u for u in users if u != "admin"]
            if deletable_users:
                user_to_delete = st.selectbox("Select a user to delete", deletable_users, key="user_to_delete")
                if st.button("Delete User"):
                    del users[user_to_delete]
                    save_users(users)
                    st.success(f"User '{user_to_delete}' deleted.")
                    st.rerun()
            else:
                st.info("No users available to delete.")

            promotable_users = [u for u, info in users.items() if info["role"] == "user"]
            if promotable_users:
                user_to_promote = st.selectbox("Select a user to promote to admin", promotable_users, key="user_to_promote")
                if st.button("Promote to Admin"):
                    users[user_to_promote]["role"] = "admin"
                    save_users(users)
                    st.success(f"User '{user_to_promote}' promoted to admin.")
                    st.rerun()
            else:
                st.info("No users available to promote.")

        else:
            st.success(f"✅ Logged in as: {st.session_state.username}")
            st.header("🎉 User Dashboard")
            st.write("Welcome to your user area!")

        # Logout Button
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

    # --- RETURN for main.py ---
    return (
        st.session_state.get("logged_in", False),
        st.session_state.get("username", ""),
        st.session_state.get("role", "user"),
    )


if __name__ == "__main__":
    show_login_system()
