import streamlit as st
from login import show_login_system
from quiz import show_quiz_app
from admin import show_admin_dashboard

def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"

    if st.session_state.page == "login":
        logged_in, username, role = show_login_system()
        if logged_in:
            if role == "admin":
                st.session_state.page = "admin"
            else:
                st.session_state.page = "quiz"
            st.rerun()

    elif st.session_state.page == "quiz":
        show_quiz_app()

    elif st.session_state.page == "admin":
        show_admin_dashboard()

if __name__ == "__main__":
    main()
