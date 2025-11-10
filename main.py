import subprocess
import sys
import os
import signal
import time

# ---------------------------
#  GLOBAL PROCESS HANDLERS
# ---------------------------
face_proc = None
voice_proc = None
quiz_proc = None


# ---------------------------
#  START MONITORING
# ---------------------------
def start_monitoring():
    global face_proc, voice_proc

    face_path = os.path.join("detection", "face.py")
    voice_path = os.path.join("detection", "voice.py")

    print("✅ Starting face detection...")
    face_proc = subprocess.Popen([sys.executable, face_path])

    print("✅ Starting voice detection...")
    voice_proc = subprocess.Popen([sys.executable, voice_path])


# ---------------------------
#  STOP MONITORING
# ---------------------------
def stop_monitoring():
    global face_proc, voice_proc

    print("\n🛑 Stopping monitoring...")

    try:
        if face_proc and face_proc.poll() is None:
            face_proc.terminate()
            print("✅ face.py stopped")
    except:
        pass

    try:
        if voice_proc and voice_proc.poll() is None:
            voice_proc.terminate()
            print("✅ voice.py stopped")
    except:
        pass


# ---------------------------
#  RUN QUIZ
# ---------------------------
def run_quiz():
    global quiz_proc

    quiz_path = os.path.join("tkinter", "quiz_file.py")
    print("🎯 Launching Quiz...")

    quiz_proc = subprocess.Popen([sys.executable, quiz_path])

    # ✅ Wait until the quiz window is closed
    while quiz_proc.poll() is None:
        time.sleep(0.5)

    print("✅ Quiz closed!")


# ---------------------------
#  MAIN EXECUTION
# ---------------------------
if __name__ == "__main__":
    print("🚀 Starting Full Exam System...")

    start_monitoring()
    run_quiz()
    stop_monitoring()

    print("✅ System Finished. Goodbye!")
