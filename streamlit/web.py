import streamlit as st
import subprocess
import sys
import os
import time
import signal

from login import show_login_system
from quiz import show_quiz_app
from admin import show_admin_dashboard

# ✅ PATH FIX
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

FACE_PATH = os.path.join(PROJECT_ROOT, "detection", "face.py")
VOICE_PATH = os.path.join(PROJECT_ROOT, "detection", "voice.py")

STOP_FILE = os.path.join(PROJECT_ROOT, "monitor_stop.flag")


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def _kill(proc):
    if not proc:
        return
    try:
        proc.terminate()
        proc.wait(timeout=1)
    except:
        try:
            proc.kill()
        except:
            pass


def stop_monitoring():
    # tell scripts to stop sitting loops
    try:
        with open(STOP_FILE, "w") as f:
            f.write("stop")
    except:
        pass

    time.sleep(0.5)

    if "face_proc" in st.session_state:
        _kill(st.session_state.face_proc)
        del st.session_state.face_proc

    if "voice_proc" in st.session_state:
        _kill(st.session_state.voice_proc)
        del st.session_state.voice_proc

    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)


def start_monitoring():
    stop_monitoring()

    # Auto clean start
    face_proc = subprocess.Popen([sys.executable, FACE_PATH])
    voice_proc = subprocess.Popen([sys.executable, VOICE_PATH])

    st.session_state.face_proc = face_proc
    st.session_state.voice_proc = voice_proc


def monitoring_running():
    p1 = st.session_state.get("face_proc")
    p2 = st.session_state.get("voice_proc")
    return (
        p1 is not None and p1.poll() is None
        and p2 is not None and p2.poll() is None
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if not st.session_state.get("logged_in", False):
        st.session_state.page = "login"

    # ✅ LOGIN PAGE
    if st.session_state.page == "login":

        logged_in, username, role = show_login_system()

        if logged_in:
            st.session_state.page = "admin" if role == "admin" else "quiz"
            st.rerun()

    # ✅ ADMIN PAGE
    elif st.session_state.page == "admin":
        show_admin_dashboard()

        if not st.session_state.get("logged_in"):
            stop_monitoring()

    # ✅ QUIZ PAGE
    elif st.session_state.page == "quiz":

        show_quiz_app()

        # ✅ Auto start monitoring when first question appears
        if st.session_state.get("quiz_started") and not monitoring_running():
            start_monitoring()

        # ✅ Stop monitoring when quiz completed
        if st.session_state.get("quiz_completed"):
            stop_monitoring()

        # ✅ Logout inside quiz.py
        if not st.session_state.get("logged_in"):
            stop_monitoring()


if __name__ == "__main__":
    main()
