import streamlit as st
import json
import os
import hashlib

# ---------- Utility Functions ----------

def load_users():
    """Load users from JSON file."""
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    """Save users to JSON file."""
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Return SHA256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password, users):
    """Verify username and password."""
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

# ---------- Streamlit UI ----------
st.set_page_config(page_title="User Login", page_icon="🤑", layout="centered")
st.title("🔐 Streamlit Login System")

# Load existing users
users = load_users()

# Maintain login session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login Section / Part 
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if verify_user(username, password, users):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Create a new account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if new_username in users:
                st.warning("Username already exists! Try another.")
            elif new_password != confirm_password:
                st.warning("Passwords do not match.")
            elif len(new_username) < 3 or len(new_password) < 3:
                st.warning("Username and password must be at least 3 characters.")
            else:
                users[new_username] = {"password": hash_password(new_password)}
                save_users(users)
                st.success("Account created successfully! You can now login.")
else:
    st.success(f"✅ Logged in as: {st.session_state.username}")
    st.write("QUIZ APP conentent will come here !")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
