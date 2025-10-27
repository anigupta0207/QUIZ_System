import sounddevice as sd
import numpy as np
import time
import os

# Create folder to store audio captures (optional)
os.makedirs('audio_captures', exist_ok=True)

# Set parameters
duration = 1  # seconds for each check
threshold = 0.05  # sensitivity level (adjust as needed)
print("🎧 Listening for loud sounds... (press Ctrl+C to stop)")

while True:
    # Record short audio snippet
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()

    # Measure volume (RMS)
    volume_norm = np.linalg.norm(recording) / len(recording)

    if volume_norm > threshold:
        print(f"🔊 Sound detected! Volume level: {volume_norm:.3f}")
        
        # Optional: Save recording
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'audio_captures/sound_{timestamp}.wav'
        sd.write(filename, recording, 44100)
        print(f"🎙️ Saved: {filename}")
    else:
        print("...quiet...")

    time.sleep(0.5)  # wait before next check
