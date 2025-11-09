import streamlit as st
import subprocess
import sys

from login import show_login_system
from quiz import show_quiz_app
from admin import show_admin_dashboard


# ========== PROCESS CONTROL ==========
def start_monitoring():
    """Start face.py and voice.py as background processes."""
    if "face_proc" not in st.session_state:
        st.session_state.face_proc = subprocess.Popen([sys.executable, "detection/face.py"])

    if "voice_proc" not in st.session_state:
        st.session_state.voice_proc = subprocess.Popen([sys.executable, "detection/voice.py"])


def stop_monitoring():
    """Stop face.py and voice.py background processes."""
    if "face_proc" in st.session_state:
        st.session_state.face_proc.terminate()
        st.session_state.face_proc = None
        del st.session_state.face_proc

    if "voice_proc" in st.session_state:
        st.session_state.voice_proc.terminate()
        st.session_state.voice_proc = None
        del st.session_state.voice_proc


# ========== MAIN APP ==========
def main():
    # Default page
    if "page" not in st.session_state:
        st.session_state.page = "login"

    # Redirect if not logged in
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"

    # --------------------------------------
    # ✅ LOGIN PAGE
    # --------------------------------------
    if st.session_state.page == "login":
        logged_in, username, role = show_login_system()

        if logged_in:
            # Admin goes to admin panel (NO MONITORING)
            if role == "admin":
                st.session_state.page = "admin"
                st.rerun()

            # Normal user → goes to quiz selection page
            else:
                st.session_state.page = "quiz"
                st.session_state.quiz_started = False  # user hasn't started quiz yet
                st.rerun()

    # --------------------------------------
    # ✅ QUIZ PAGE (User Only)
    # --------------------------------------
    elif st.session_state.page == "quiz":

        # Monitoring starts ONLY AFTER user clicks "Start Quiz"
        if st.session_state.get("quiz_started", False):
            st.info("🟢 Face & Voice Monitoring Running")
            start_monitoring()
        else:
            st.warning("🔴 Monitoring Not Started Yet")

        quiz_completed = show_quiz_app()

        # ✅ When quiz completes, stop monitoring
        if quiz_completed:
            stop_monitoring()
            st.session_state.quiz_started = False

        # User logs out → stop monitoring
        if not st.session_state.get("logged_in", False):
            stop_monitoring()

    # --------------------------------------
    # ✅ ADMIN PAGE (NO MONITORING)
    # --------------------------------------
    elif st.session_state.page == "admin":
        show_admin_dashboard()

        # Admin logout
        if not st.session_state.get("logged_in", False):
            stop_monitoring()  # extra safety
            st.rerun()


if __name__ == "__main__":
    main()
