import sounddevice as sd
import numpy as np
import time
import os
import soundfile as sf
import winsound

# === Setup ===
os.makedirs('audio_captures', exist_ok=True)

# === Calibration Phase ===
def calibrate_background(duration=4):
    print(f" Calibrating ambient noise for {duration} seconds... Please stay quiet.")
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()

    # Compute RMS (Root Mean Square)
    bg_level = np.sqrt(np.mean(recording ** 2))
    print(f" Average background noise level: {bg_level:.6f}")
    return bg_level

def detect_sound(threshold, duration=1):
    print("\n Voice detection started! (Press Ctrl+C to stop)\n")

    while True:
        try:
            recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
            sd.wait()

            volume = np.sqrt(np.mean(recording ** 2))

            if volume > threshold:
                print(f"Sound detected! Volume: {volume:.4f}")

                timestamp = time.strftime('%d_%H%M%S')
                filename = f'audio_captures/sound_{timestamp}.wav'
                sf.write(filename, recording, 44100)
                print(f"Saved: {filename}")

                winsound.Beep(1000, 300)

            else:
                print(f"...quiet... ({volume:.5f})")

            time.sleep(0.5)

        except Exception as e:
            print("error:", e)
            time.sleep(1)

try:
    bg_level = calibrate_background(duration=4)
    threshold = bg_level * 1.5  
    detect_sound(threshold)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
except Exception as e:
    print("Error:", e)
