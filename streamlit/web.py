import streamlit as st
import subprocess
import sys
import os
import time
import signal

# Import your app modules
from login import show_login_system
from quiz import show_quiz_app
from admin import show_admin_dashboard

# ---------------------------------------
# ✅ PATH FIX (IMPORTANT!!)
# ---------------------------------------
# This file is inside: QUIZ_System/streamlit/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go one folder up → QUIZ_System/
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

FACE_PATH = os.path.join(PROJECT_ROOT, "detection", "face.py")
VOICE_PATH = os.path.join(PROJECT_ROOT, "detection", "voice.py")

STOP_FILE = os.path.join(PROJECT_ROOT, "monitor_stop.flag")


# ---------------------------------------
# ✅ START MONITORING
# ---------------------------------------
def start_monitoring():

    # Remove old stop file
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)

    # Start face.py once
    if "face_proc" not in st.session_state:
        st.session_state.face_proc = subprocess.Popen(
            [sys.executable, FACE_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Start voice.py once
    if "voice_proc" not in st.session_state:
        st.session_state.voice_proc = subprocess.Popen(
            [sys.executable, VOICE_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


# ---------------------------------------
# ✅ TERMINATE PROCESS HELPER
# ---------------------------------------
def _kill_process(proc):
    try:
        proc.terminate()
        proc.wait(timeout=1)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ---------------------------------------
# ✅ STOP MONITORING
# ---------------------------------------
def stop_monitoring():
    # Tell the scripts to stop themselves
    with open(STOP_FILE, "w") as f:
        f.write("stop")

    time.sleep(0.6)  # give time to exit gracefully

    # Kill face process if still running
    if "face_proc" in st.session_state:
        _kill_process(st.session_state.face_proc)
        del st.session_state.face_proc

    # Kill voice process if still running
    if "voice_proc" in st.session_state:
        _kill_process(st.session_state.voice_proc)
        del st.session_state.voice_proc

    # Delete stop flag
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)


# ---------------------------------------
# ✅ MAIN APP
# ---------------------------------------
def main():

    # Default page = login
    if "page" not in st.session_state:
        st.session_state.page = "login"

    # If logged out, force login page
    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"

    # -------------------------
    # ✅ LOGIN PAGE
    # -------------------------
    if st.session_state.page == "login":

        logged_in, username, role = show_login_system()

        if logged_in:

            # Start face & voice monitoring only for normal users
            if role != "admin":
                start_monitoring()

            # Switch page
            st.session_state.page = "admin" if role == "admin" else "quiz"

            st.rerun()

    # -------------------------
    # ✅ QUIZ PAGE
    # -------------------------
    elif st.session_state.page == "quiz":

        show_quiz_app()

        # If quiz finished -> stop monitoring
        if st.session_state.get("quiz_completed", False):
            stop_monitoring()

        # If user logged out inside quiz.py
        if not st.session_state.get("logged_in", False):
            stop_monitoring()

    # -------------------------
    # ✅ ADMIN PAGE
    # -------------------------
    elif st.session_state.page == "admin":

        show_admin_dashboard()

        # If admin logs out
        if not st.session_state.get("logged_in", False):
            stop_monitoring()


# ---------------------------------------
if __name__ == "__main__":
    main()
