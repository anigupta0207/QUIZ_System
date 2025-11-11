import streamlit as st
import json, os, hashlib, re

# ---------- Utility ----------
def load_users():
    if not os.path.exists("users.json"):
        json.dump({}, open("users.json", "w"))
    return json.load(open("users.json"))

def save_users(users):
    json.dump(users, open("users.json", "w"), indent=4)

def hash_password(p): 
    return hashlib.sha256(p.encode()).hexdigest()

def verify_user(u, p, users): 
    return u in users and users[u]["password"] == hash_password(p)


# ---------- App ----------
def show_login_system():
    st.set_page_config(page_title="PrepSecure", layout="wide")

    # ---------- Custom Style ----------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #0f0f1a;
        color: white;
    }

    .left-img {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 0 25px rgba(0,0,0,0.5);
    }

    .left-img img {
        width: 100%;
        height: 85vh;
        object-fit: cover;
        border-radius: 15px;
    }

    .overlay-text {
        position: relative;
        bottom: 90px;
        left: 30px;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        text-shadow: 0 3px 10px rgba(0,0,0,0.8);
    }

    /* 🔹 Added spacing between image and form */
    .right-section {
        margin-left: 3rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: left;
        border-bottom: 1px solid #444;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #bbb;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #fff;
    }

    .stTabs [aria-selected="true"] {
        color: white !important;
    }

    .stTextInput>div>div>input, .stPasswordInput>div>div>input {
        background-color: #1f1f2e;
        color: white;
        border-radius: 8px;
        border: none;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #8b5cf6, #6366f1);
        color: white;
        border: none;
        padding: 0.6rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }

    /* ---------- Soft Fade-In Animation ---------- */
    @keyframes fadeIn {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .container, .card, .right-side, .left-side {
        opacity: 0;
        animation: fadeIn 1s ease-out forwards;
    }

    /* Add subtle delays for a staggered entrance */
    .card {
        animation-delay: 0.2s;
    }
    .left-side {
        animation-delay: 0.4s;
    }
    .right-side {
        animation-delay: 0.6s;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------- Users ----------
    users = load_users()
    if "admin" not in users:
        users["admin"] = {"password": hash_password("admin123"), "role": "admin"}
        save_users(users)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # ---------- Layout ----------
    left, space, right = st.columns([0.9, 0.15, 0.9])  # Added middle spacing column

    with left:
        st.markdown(
            """
            <div class="left-img left-side">
                <img src="https://images.unsplash.com/photo-1519389950473-47ba0277781c" alt="background">
                <div class="overlay-text">
                    Capturing Moments,<br>Creating Memories
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="right-section right-side">', unsafe_allow_html=True)

        st.title("PrepSecure")
        st.subheader("Access your account")
        st.write("")

        # ---------- Tabs ----------
        if not st.session_state.logged_in:
            tab1, tab2, tab3 = st.tabs(["🔑 Sign In", "📝 Sign Up", "👨🏻‍💼 Admin Login"])

            # -------------------- SIGN IN --------------------
            with tab1:
                st.subheader("Sign In to your account")
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Sign In"):
                    if verify_user(u, p, users):
                        if users[u]["role"] == "admin":
                            st.warning("Use Admin tab for admin access.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.username = u
                            st.session_state.role = "user"
                            st.success(f"Welcome back, {u}!")
                            st.rerun()
                    else:
                        st.error("Invalid username or password.")

            # -------------------- SIGN UP --------------------
            with tab2:
                st.subheader("Create a new account")
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                cp = st.text_input("Confirm Password", type="password")

                if st.button("Sign Up"):
                    valid_username = re.fullmatch(r"[A-Za-z0-9_]+", nu)
                    if nu in users:
                        st.warning("Username already exists!")
                    elif np != cp:
                        st.warning("Passwords do not match.")
                    elif not valid_username:
                        st.warning("Username can only contain letters, numbers, and underscores.")
                    elif len(nu) < 3 or len(np) < 3:
                        st.warning("Username and password must be at least 3 characters.")
                    else:
                        users[nu] = {"password": hash_password(np), "role": "user"}
                        save_users(users)
                        st.success("Account created successfully! You can now login.")

            # -------------------- ADMIN LOGIN --------------------
            with tab3:
                st.subheader("Admin Login")
                au = st.text_input("Admin Username")
                ap = st.text_input("Admin Password", type="password")

                if st.button("Admin Login"):
                    if verify_user(au, ap, users) and users[au]["role"] == "admin":
                        st.session_state.logged_in = True
                        st.session_state.username = au
                        st.session_state.role = "admin"
                        st.success(f"Welcome Admin, {au}!")
                        st.rerun()
                    else:
                        st.error("Invalid admin credentials.")
        else:
            # Logged in view
            st.header(f"Welcome, {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.role = ""
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # close right-section

    # --- RETURN for web.py ---
    return (
        st.session_state.get("logged_in", False),
        st.session_state.get("username", ""),
        st.session_state.get("role", "user"),
    )


if __name__ == "__main__":
    show_login_system()
