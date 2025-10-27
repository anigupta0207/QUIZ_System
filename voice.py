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
    print(f"🎚️ Calibrating ambient noise for {duration} seconds... Please stay quiet.")
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()

    # Compute RMS (Root Mean Square)
    background_level = np.sqrt(np.mean(recording ** 2))
    print(f"📊 Average background noise level: {background_level:.6f}")
    return background_level

# === Continuous Detection Phase ===
def detect_sound(threshold, duration=1):
    print("\n🎧 Voice detection started! (Press Ctrl+C to stop)\n")

    while True:
        try:
            # Record short snippet
            recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
            sd.wait()

            # Compute volume level
            volume_norm = np.sqrt(np.mean(recording ** 2))

            if volume_norm > threshold:
                print(f"🔊 Sound detected! Volume: {volume_norm:.4f} (threshold: {threshold:.4f})")

                # Save detected sound clip
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'audio_captures/sound_{timestamp}.wav'
                sf.write(filename, recording, 44100)
                print(f"🎙️ Saved: {filename}")

                # ⚠️ ALERT BEEP (non-blocking short beep)
                winsound.Beep(1000, 300)

            else:
                print(f"...quiet... ({volume_norm:.5f})")

            # Keep checking continuously (0.5s gap)
            time.sleep(0.5)

        except Exception as e:
            print("⚠️ Runtime error:", e)
            time.sleep(1)

# === Main Program ===
try:
    background_level = calibrate_background(duration=4)
    threshold = background_level * 1.5  # Adjust multiplier for sensitivity
    detect_sound(threshold)

except KeyboardInterrupt:
    print("\n🛑 Program stopped by user.")
except Exception as e:
    print("⚠️ Error:", e)
