import sounddevice as sd
import numpy as np
import time
import os
import soundfile as sf
import signal
import sys

# ✅ Shutdown handler for Streamlit stop
stop_signal = False
def handle_exit(signum, frame):
    global stop_signal
    stop_signal = True

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# ✅ Mac-Friendly Beep Function
def play_beep():
    # macOS beep using terminal bell
    print("\a")   # ASCII bell, works on Mac terminal
    sys.stdout.flush()

# ✅ Ensure audio folder exists
base_dir = os.path.dirname(os.path.abspath(__file__))
capture_dir = os.path.join(base_dir, "audio_captures")
os.makedirs(capture_dir, exist_ok=True)

# ✅ Calibrate background noise
def calibrate_background(duration=4):
    print(f"🔊 Calibrating ambient noise for {duration} seconds... please stay quiet.")
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()

    bg_level = np.sqrt(np.mean(recording ** 2))
    print(f"✅ Background noise level: {bg_level:.6f}")
    return bg_level

# ✅ Sound detection loop
def detect_sound(threshold, duration=1):
    print("\n🎤 Voice monitoring started! (auto-stops when quiz ends)\n")

    while not stop_signal:
        try:
            # record a small chunk
            recording = sd.rec(
                int(duration * 44100), 
                samplerate=44100, 
                channels=1, 
                dtype='float64'
            )
            sd.wait()

            volume = np.sqrt(np.mean(recording ** 2))

            if stop_signal:
                print("🛑 Voice monitoring stopping...")
                break

            if volume > threshold:
                print(f"⚠️ Sound detected! Volume: {volume:.4f}")

                timestamp = time.strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(capture_dir, f"sound_{timestamp}.wav")

                sf.write(file_path, recording, 44100)
                print(f"💾 Saved suspicious audio: {file_path}")

                play_beep()

            else:
                print(f"...quiet... ({volume:.6f})")

            time.sleep(0.4)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(1)

try:
    bg = calibrate_background(4)
    threshold = bg * 1.5  # sensitivity
    detect_sound(threshold)

except Exception as e:
    print("❌ Fatal Error:", e)

print("✅ Voice monitor closed cleanly")
