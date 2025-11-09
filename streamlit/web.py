import streamlit as st
from login import show_login_system
from quiz import show_quiz_app

# Main application router
def main():
    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"
    
    # Page router
    if st.session_state.page == "login":
        logged_in, username = show_login_system()
        if logged_in:
            st.session_state.page = "quiz"
            st.rerun()
    elif st.session_state.page == "quiz":
        show_quiz_app()

if __name__ == "__main__":
    main()