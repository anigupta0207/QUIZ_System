import streamlit as st
import subprocess
import sys

from login import show_login_system
from quiz import show_quiz_app
from admin import show_admin_dashboard


# ========== PROCESS CONTROL ==========
def start_monitoring():
    """Start face.py and voice.py in background."""
    if "face_proc" not in st.session_state:
        st.session_state.face_proc = subprocess.Popen([sys.executable, "detection/face.py"])
    if "voice_proc" not in st.session_state:
        st.session_state.voice_proc = subprocess.Popen([sys.executable, "detection/voice.py"])


def stop_monitoring():
    """Stop face.py and voice.py background processes."""
    if "face_proc" in st.session_state:
        st.session_state.face_proc.terminate()
        del st.session_state.face_proc

    if "voice_proc" in st.session_state:
        st.session_state.voice_proc.terminate()
        del st.session_state.voice_proc


# ========== MAIN APP ==========
def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"

    # ========== LOGIN PAGE ==========
    if st.session_state.page == "login":
        logged_in, username, role = show_login_system()

        if logged_in:

            # ✅ START MONITORING ONLY FOR NORMAL USERS  
            if role != "admin":
                start_monitoring()

            # Page switching
            if role == "admin":
                st.session_state.page = "admin"
            else:
                st.session_state.page = "quiz"

            st.rerun()

    # ========== QUIZ PAGE (Users Only) ==========
    elif st.session_state.page == "quiz":
        st.info("🟢 Face & Voice Monitoring Running")
        show_quiz_app()

        if not st.session_state.get("logged_in", False):
            stop_monitoring()

    # ========== ADMIN PAGE (NO MONITORING) ==========
    elif st.session_state.page == "admin":
        show_admin_dashboard()

        # ✅ Admin logout should NOT stop anything (because admin never started monitoring)
        # but if something exists accidentally, we clean it.
        if not st.session_state.get("logged_in", False):
            stop_monitoring()


if __name__ == "__main__":
    main()
